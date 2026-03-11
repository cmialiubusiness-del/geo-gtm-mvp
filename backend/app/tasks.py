from __future__ import annotations

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.enums import RunProvider
from app.db import SessionLocal
from app.models import Organization
from app.services.pipeline import execute_run_for_provider


@celery_app.task(name="app.tasks.run_collection_for_org")
def run_collection_for_org(org_id: int, provider: str, brand_id: int | None = None) -> dict[str, int | str]:
    with SessionLocal() as db:
        run = execute_run_for_provider(db, org_id, RunProvider(provider), brand_id=brand_id)
        return {"org_id": org_id, "provider": provider, "run_id": run.id, "brand_id": run.brand_id}


@celery_app.task(name="app.tasks.run_nightly_all_orgs")
def run_nightly_all_orgs() -> dict[str, int]:
    dispatched = 0
    with SessionLocal() as db:
        orgs = list(db.scalars(select(Organization).order_by(Organization.id.asc())))
        for org in orgs:
            for brand in org.brands:
                for provider in RunProvider:
                    run_collection_for_org.delay(org.id, provider.value, brand.id)
                    dispatched += 1
    return {"dispatched": dispatched}
