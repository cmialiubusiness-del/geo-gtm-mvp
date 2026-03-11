from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.deps import get_current_user, get_db
from app.models import Report, User
from app.schemas import MonthlyReportRequest, ReportResponse, WeeklyReportRequest
from app.services.reports import generate_report
from app.core.enums import ReportType

router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/weekly", response_model=ReportResponse)
def create_weekly_report(
    payload: WeeklyReportRequest,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    report = generate_report(
        db,
        current_user.org_id,
        ReportType.weekly_brief,
        brand_id=brand_id,
        week_start=payload.week_start,
    )
    return ReportResponse.model_validate(report)


@router.post("/monthly", response_model=ReportResponse)
def create_monthly_report(
    payload: MonthlyReportRequest,
    brand_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ReportResponse:
    report = generate_report(
        db,
        current_user.org_id,
        ReportType.monthly_strategy,
        brand_id=brand_id,
        month=payload.month,
    )
    return ReportResponse.model_validate(report)


@router.get("", response_model=list[ReportResponse])
def list_reports(
    brand_id: int | None = None,
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> list[ReportResponse]:
    stmt = select(Report).where(Report.org_id == current_user.org_id)
    if brand_id is not None:
        stmt = stmt.where(Report.brand_id == brand_id)
    reports = list(db.scalars(stmt.order_by(Report.created_at.desc())))
    return [ReportResponse.model_validate(item) for item in reports]


@router.get("/{report_id}/download")
def download_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> FileResponse:
    report = db.scalar(
        select(Report).where(Report.id == report_id, Report.org_id == current_user.org_id)
    )
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告不存在")

    file_path = Path(report.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="报告文件不存在")
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=file_path.name,
    )
