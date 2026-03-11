from __future__ import annotations

from fastapi import APIRouter

from app.services.analysis_framework import get_analysis_framework
from app.services.project_factory import industry_options

router = APIRouter(prefix="/meta", tags=["meta"])


@router.get("/industries")
def industries() -> dict[str, list[str]]:
    return {"items": industry_options()}


@router.get("/analysis-framework")
def analysis_framework() -> dict[str, object]:
    return get_analysis_framework()
