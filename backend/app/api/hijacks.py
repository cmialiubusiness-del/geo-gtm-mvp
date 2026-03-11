from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.services.metrics import list_hijacks
from app.services.provider_scope import normalize_provider_selector

router = APIRouter(prefix="/hijacks", tags=["hijacks"])


@router.get("")
def hijacks(
    range: str = "last_run",
    provider: str = "all",
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, object]:
    try:
        provider = normalize_provider_selector(provider)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return list_hijacks(db, current_user.org_id, range, provider, brand_id=brand_id)
