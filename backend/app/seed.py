from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select

from app.core.config import settings
from app.core.enums import RunProvider, UserRole
from app.core.security import get_password_hash
from app.db import SessionLocal
from app.models import Brand, Organization, Run, User
from app.services.pipeline import execute_run_for_provider
from app.services.project_factory import ensure_brand_project_assets


def _ensure_demo_org() -> tuple[int, int]:
    with SessionLocal() as db:
        org = db.scalar(
            select(Organization).where(Organization.name == "Demo香港跨境服务")
        )
        if not org:
            org = Organization(name="Demo香港跨境服务")
            db.add(org)
            db.flush()

        user = db.scalar(select(User).where(User.email == "demo@example.com"))
        if not user:
            db.add(
                User(
                    org_id=org.id,
                    email="demo@example.com",
                    password_hash=get_password_hash("demo1234"),
                    role=UserRole.admin,
                )
            )

        brand = db.scalar(select(Brand).where(Brand.org_id == org.id))
        if not brand:
            brand = Brand(
                org_id=org.id,
                name="港X顾问",
                aliases=["港X", "港X咨询", "港X跨境"],
                project_context="跨境贸易与服务",
            )
            db.add(brand)
            db.flush()
        brand.project_context = "跨境贸易与服务"

        brands = list(db.scalars(select(Brand).where(Brand.org_id == org.id).order_by(Brand.id.asc())))
        for item in brands:
            if item.id == brand.id:
                item.project_context = "跨境贸易与服务"
            elif not item.project_context:
                item.project_context = "通用行业"
            ensure_brand_project_assets(db, org.id, item)

        db.commit()
        return org.id, brand.id


def _ensure_historical_runs(org_id: int, brand_id: int) -> None:
    with SessionLocal() as db:
        provider_counts = {
            provider: int(
                db.scalar(
                    select(func.count(Run.id)).where(
                        Run.org_id == org_id, Run.brand_id == brand_id, Run.provider == provider
                    )
                )
                or 0
            )
            for provider in RunProvider
        }

    base_dates = [
        datetime.now(timezone.utc) - timedelta(days=21),
        datetime.now(timezone.utc) - timedelta(days=10),
    ]
    offsets = {provider: index * 2 for index, provider in enumerate(RunProvider)}
    for provider in RunProvider:
        missing = max(0, 2 - provider_counts.get(provider, 0))
        if missing <= 0:
            continue
        for base_date in base_dates:
            if missing <= 0:
                break
            started_at = base_date + timedelta(hours=offsets[provider])
            finished_at = started_at + timedelta(minutes=4)
            with SessionLocal() as db:
                execute_run_for_provider(
                    db,
                    org_id,
                    provider,
                    brand_id=brand_id,
                    started_at=started_at,
                    finished_at=finished_at,
                )
            missing -= 1


def seed_data() -> None:
    if not settings.seed_demo:
        return
    org_id, brand_id = _ensure_demo_org()
    _ensure_historical_runs(org_id, brand_id)


if __name__ == "__main__":
    seed_data()
