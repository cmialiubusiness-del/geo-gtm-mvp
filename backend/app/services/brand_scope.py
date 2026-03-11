from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Brand


def list_org_brands(db: Session, org_id: int) -> list[Brand]:
    return list(
        db.scalars(
            select(Brand).where(Brand.org_id == org_id).order_by(Brand.id.asc())
        )
    )


def resolve_brand(db: Session, org_id: int, brand_id: int | None = None) -> Brand | None:
    if brand_id is not None:
        return db.scalar(
            select(Brand).where(Brand.org_id == org_id, Brand.id == brand_id)
        )
    return db.scalar(select(Brand).where(Brand.org_id == org_id).order_by(Brand.id.asc()))
