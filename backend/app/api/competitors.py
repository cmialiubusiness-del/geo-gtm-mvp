from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Competitor, User
from app.schemas import CompetitorCreate, CompetitorResponse
from app.services.brand_scope import resolve_brand
from app.services.project_factory import (
    MAX_COMPETITORS_PER_BRAND,
    ensure_brand_project_assets,
    recommend_real_competitors,
    search_real_competitors,
)

router = APIRouter(prefix="/competitors", tags=["competitors"])


@router.get("", response_model=list[CompetitorResponse])
def list_competitors(
    brand_id: int | None = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[CompetitorResponse]:
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        return []
    ensure_brand_project_assets(db, current_user.org_id, brand)
    db.commit()
    competitors = list(
        db.scalars(
            select(Competitor)
            .where(Competitor.org_id == current_user.org_id, Competitor.brand_id == brand.id)
            .order_by(Competitor.id.asc())
        )
    )
    return [CompetitorResponse.model_validate(item) for item in competitors]


@router.post("", response_model=CompetitorResponse)
def create_competitor(
    payload: CompetitorCreate,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompetitorResponse:
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="竞品名称不能为空")
    existing = list(
        db.scalars(
            select(Competitor).where(
                Competitor.org_id == current_user.org_id, Competitor.brand_id == brand.id
            )
        )
    )
    existing_names = {item.name.lower() for item in existing}
    if name.lower() in existing_names:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="竞品已存在")
    if len(existing) >= MAX_COMPETITORS_PER_BRAND:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"单个项目最多支持 {MAX_COMPETITORS_PER_BRAND} 个竞品",
        )
    competitor = Competitor(
        org_id=current_user.org_id,
        brand_id=brand.id,
        name=name,
        aliases=payload.aliases,
    )
    db.add(competitor)
    db.commit()
    db.refresh(competitor)
    return CompetitorResponse.model_validate(competitor)


@router.get("/suggestions")
def suggestions(
    brand_id: int | None = None,
    limit: int = 8,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")
    ensure_brand_project_assets(db, current_user.org_id, brand)
    db.commit()
    existing_names = {
        item.name.lower()
        for item in db.scalars(
            select(Competitor).where(
                Competitor.org_id == current_user.org_id, Competitor.brand_id == brand.id
            )
        )
    }
    candidates = [
        item
        for item in recommend_real_competitors(brand.name, brand.project_context, limit=max(limit, 1) + 6)
        if str(item["name"]).lower() not in existing_names
    ][: max(limit, 1)]
    return {"brand_id": brand.id, "items": candidates}


@router.get("/search")
def search(
    q: str,
    brand_id: int | None = None,
    limit: int = 12,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    brand = resolve_brand(db, current_user.org_id, brand_id=brand_id)
    if not brand:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="品牌项目不存在")
    ensure_brand_project_assets(db, current_user.org_id, brand)
    db.commit()
    existing_names = {
        item.name.lower()
        for item in db.scalars(
            select(Competitor).where(
                Competitor.org_id == current_user.org_id, Competitor.brand_id == brand.id
            )
        )
    }
    candidates = [
        item
        for item in search_real_competitors(
            brand.name,
            query=q,
            project_context=brand.project_context,
            limit=max(limit, 1) + 6,
        )
        if str(item["name"]).lower() not in existing_names
    ][: max(limit, 1)]
    return {"brand_id": brand.id, "items": candidates}


@router.delete("/{competitor_id}")
def delete_competitor(
    competitor_id: int,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, str]:
    stmt = select(Competitor).where(
        Competitor.id == competitor_id, Competitor.org_id == current_user.org_id
    )
    if brand_id is not None:
        stmt = stmt.where(Competitor.brand_id == brand_id)
    competitor = db.scalar(stmt)
    if not competitor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="竞品不存在")
    db.delete(competitor)
    db.commit()
    return {"status": "deleted"}
