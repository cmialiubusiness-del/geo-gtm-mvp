from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import User
from app.schemas import ProjectsOverviewResponse
from app.services.brand_scope import list_org_brands
from app.services.metrics import build_projects_overview
from app.services.project_factory import ensure_brand_project_assets, merge_duplicate_brands

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("/overview", response_model=ProjectsOverviewResponse)
def projects_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectsOverviewResponse:
    if merge_duplicate_brands(db, current_user.org_id):
        db.commit()
    brands = list_org_brands(db, current_user.org_id)
    for brand in brands:
        ensure_brand_project_assets(db, current_user.org_id, brand)
    db.commit()
    payload = build_projects_overview(db, current_user.org_id)
    return ProjectsOverviewResponse.model_validate(payload)
