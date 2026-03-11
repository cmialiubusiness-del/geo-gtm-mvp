from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.schemas import ClaimResponse
from app.services.metrics import get_claim_detail, list_claims
from app.services.provider_scope import normalize_provider_selector

router = APIRouter(prefix="/claims", tags=["claims"])


@router.get("", response_model=list[ClaimResponse])
def claims(
    provider: str = "all",
    brand_id: int | None = None,
    category: str | None = None,
    risk_level: str | None = None,
    subject_type: str | None = None,
    search: str | None = None,
    limit: int = 200,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ClaimResponse]:
    try:
        provider = normalize_provider_selector(provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    rows = list_claims(
        db,
        current_user.org_id,
        provider=provider,
        brand_id=brand_id,
        category=category,
        risk_level=risk_level,
        subject_type=subject_type,
        search=search,
        limit=limit,
    )
    return [ClaimResponse.model_validate(row) for row in rows]


@router.get("/{claim_id}", response_model=ClaimResponse)
def claim_detail(
    claim_id: int,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ClaimResponse:
    row = get_claim_detail(db, current_user.org_id, claim_id, brand_id=brand_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="断言不存在")
    return ClaimResponse.model_validate(row)
