from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.enums import RunProvider, RunStatus
from app.deps import get_current_user, get_db
from app.models import Answer, Brand, Claim, Hijack, Run, User
from app.schemas import RunDetailResponse, RunNowRequest, RunResponse
from app.services.pipeline import execute_run_for_provider
from app.services.brand_scope import resolve_brand
from app.services.provider_scope import normalize_provider_selector, provider_values_from_selector
from app.tasks import run_collection_for_org

router = APIRouter(prefix="/runs", tags=["runs"])


def _latest_recent_run(db: Session, org_id: int, brand_id: int | None = None) -> Run | None:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=settings.run_rate_limit_seconds)
    stmt = (
        select(Run)
        .where(Run.org_id == org_id, Run.started_at >= cutoff)
        .order_by(Run.started_at.desc())
        .limit(1)
    )
    if brand_id is not None:
        stmt = stmt.where(Run.brand_id == brand_id)
    return db.scalar(stmt)


@router.post("/run-now")
def run_now(
    payload: RunNowRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    brand = resolve_brand(db, current_user.org_id, payload.brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")

    if _latest_recent_run(db, current_user.org_id, brand.id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"触发频率受限，请在 {settings.run_rate_limit_seconds} 秒后再试",
        )

    try:
        provider_selector = normalize_provider_selector(payload.provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    providers = provider_values_from_selector(provider_selector)
    run_results: list[dict[str, object]] = []
    for provider in providers:
        try:
            task = run_collection_for_org.delay(current_user.org_id, provider, brand.id)
            run_results.append(
                {"provider": provider, "queued": True, "task_id": task.id, "brand_id": brand.id}
            )
        except Exception:
            run = execute_run_for_provider(
                db, current_user.org_id, RunProvider(provider), brand_id=brand.id
            )
            run_results.append(
                {"provider": provider, "queued": False, "run_id": run.id, "brand_id": run.brand_id}
            )
    return {"status": "accepted", "runs": run_results}


@router.get("", response_model=list[RunResponse])
def list_runs(
    brand_id: int | None = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[RunResponse]:
    stmt = select(Run).where(Run.org_id == current_user.org_id)
    if brand_id is not None:
        stmt = stmt.where(Run.brand_id == brand_id)
    runs = list(db.scalars(stmt.order_by(Run.started_at.desc()).limit(30)))
    brands = {
        brand.id: brand.name
        for brand in db.scalars(select(Brand).where(Brand.org_id == current_user.org_id))
    }
    return [
        RunResponse(
            id=item.id,
            org_id=item.org_id,
            brand_id=item.brand_id,
            brand_name=brands.get(item.brand_id, f"品牌#{item.brand_id}"),
            provider=item.provider,
            started_at=item.started_at,
            finished_at=item.finished_at,
            status=item.status,
        )
        for item in runs
    ]


@router.get("/{run_id}", response_model=RunDetailResponse)
def get_run(
    run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RunDetailResponse:
    run = db.scalar(select(Run).where(Run.id == run_id, Run.org_id == current_user.org_id))
    if not run:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="运行记录不存在")

    brand = resolve_brand(db, current_user.org_id, run.brand_id)
    answers_count = db.scalar(select(func.count(Answer.id)).where(Answer.run_id == run.id)) or 0
    claims_count = db.scalar(
        select(func.count(Claim.id)).join(Answer, Claim.answer_id == Answer.id).where(Answer.run_id == run.id)
    ) or 0
    hijacks_count = db.scalar(
        select(func.count(Hijack.id)).join(Answer, Hijack.answer_id == Answer.id).where(Answer.run_id == run.id)
    ) or 0

    return RunDetailResponse(
        id=run.id,
        org_id=run.org_id,
        brand_id=run.brand_id,
        brand_name=brand.name if brand else f"品牌#{run.brand_id}",
        provider=run.provider,
        started_at=run.started_at,
        finished_at=run.finished_at,
        status=run.status,
        answers_count=int(answers_count),
        claims_count=int(claims_count),
        hijacks_count=int(hijacks_count),
    )
