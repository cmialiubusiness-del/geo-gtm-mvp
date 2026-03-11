from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.schemas import CapabilitiesResponse, CompetitorMetricsResponse, OverviewMetricsResponse
from app.services.brand_scope import resolve_brand
from app.services.metrics import (
    build_capabilities_metrics,
    build_competitor_metrics,
    build_dimension_audit,
    build_overview_metrics,
)
from app.services.provider_scope import normalize_provider_selector
from app.services.project_factory import ensure_brand_project_assets

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _ensure_brand_ready(db: Session, org_id: int, brand_id: int | None) -> None:
    brand = resolve_brand(db, org_id, brand_id=brand_id)
    if not brand:
        return
    ensure_brand_project_assets(db, org_id, brand)
    db.commit()


def _normalize_provider_or_400(provider: str) -> str:
    try:
        return normalize_provider_selector(provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("/overview", response_model=OverviewMetricsResponse)
def overview(
    range: str = "last_run",
    provider: str = "all",
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OverviewMetricsResponse:
    provider = _normalize_provider_or_400(provider)
    _ensure_brand_ready(db, current_user.org_id, brand_id)
    return OverviewMetricsResponse.model_validate(
        build_overview_metrics(db, current_user.org_id, range, provider, brand_id=brand_id)
    )


@router.get("/capabilities", response_model=CapabilitiesResponse)
def capabilities(
    range: str = "last_run",
    provider: str = "all",
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CapabilitiesResponse:
    provider = _normalize_provider_or_400(provider)
    _ensure_brand_ready(db, current_user.org_id, brand_id)
    return CapabilitiesResponse.model_validate(
        build_capabilities_metrics(db, current_user.org_id, range, provider, brand_id=brand_id)
    )


@router.get("/competitors", response_model=CompetitorMetricsResponse)
def competitors(
    competitor_id: int | None = None,
    range: str = "last_run",
    provider: str = "all",
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CompetitorMetricsResponse:
    provider = _normalize_provider_or_400(provider)
    _ensure_brand_ready(db, current_user.org_id, brand_id)
    return CompetitorMetricsResponse.model_validate(
        build_competitor_metrics(
            db, current_user.org_id, range, provider, competitor_id, brand_id=brand_id
        )
    )


@router.get("/dimension-audit")
def dimension_audit(
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    _ensure_brand_ready(db, current_user.org_id, brand_id)
    return build_dimension_audit(db, current_user.org_id, brand_id=brand_id)
