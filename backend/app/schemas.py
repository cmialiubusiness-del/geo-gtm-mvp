from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.core.enums import (
    ClaimRiskLevel,
    ClaimSentiment,
    ClaimSubjectType,
    PromptCategory,
    PromptIntentType,
    ReportType,
    RunProvider,
    RunStatus,
    UserRole,
)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class RegisterRequest(LoginRequest):
    organization_name: str = Field(min_length=2, max_length=255)
    brand_name: str | None = None
    brand_context: str | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    organization_name: str
    email: EmailStr
    role: UserRole
    created_at: datetime


class NameAliasBase(BaseModel):
    name: str
    aliases: list[str] = Field(default_factory=list)


class BrandBase(NameAliasBase):
    project_context: str | None = None


class BrandCreate(BrandBase):
    pass


class BrandResponse(BrandBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    created_at: datetime
    project_exists: bool = False


class CompetitorCreate(NameAliasBase):
    pass


class CompetitorResponse(NameAliasBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    brand_id: int
    created_at: datetime


class PromptBase(BaseModel):
    text: str
    category: PromptCategory
    intent_type: PromptIntentType
    is_active: bool = True


class PromptResponse(PromptBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    brand_id: int
    created_at: datetime


class RunNowRequest(BaseModel):
    provider: str = "all"
    brand_id: int | None = None


class RunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    brand_id: int
    brand_name: str
    provider: RunProvider
    started_at: datetime
    finished_at: datetime | None
    status: RunStatus


class RunDetailResponse(RunResponse):
    answers_count: int
    claims_count: int
    hijacks_count: int


class ClaimResponse(BaseModel):
    id: int
    created_at: datetime
    provider: RunProvider
    prompt_id: int
    prompt_text: str
    category: PromptCategory
    subject_type: ClaimSubjectType
    subject_name: str
    claim_text: str
    sentiment: ClaimSentiment
    impact_score: int
    risk_level: ClaimRiskLevel
    raw_text: str


class HijackResponse(BaseModel):
    id: int
    created_at: datetime
    provider: RunProvider
    prompt_id: int
    prompt_text: str
    hijack_flag: bool
    hijack_strength: int
    recommended_entities: list[str]
    brand_present: bool


class OverviewMetricsResponse(BaseModel):
    range: str
    provider: str
    brand_id: int | None = None
    brand_name: str | None = None
    kpis: dict[str, float | int]
    trend: list[dict[str, Any]]


class CapabilityEntry(BaseModel):
    category: PromptCategory
    display_name: str
    definition: str
    score: float
    label: str
    top_positive_claims: list[str]
    top_negative_claims: list[str]


class CapabilitiesResponse(BaseModel):
    range: str
    provider: str
    brand_id: int | None = None
    brand_name: str | None = None
    radar: list[dict[str, Any]]
    categories: list[CapabilityEntry]


class CompetitorMetricsResponse(BaseModel):
    competitor_id: int | None
    range: str
    provider: str
    brand_id: int | None = None
    brand_name: str | None = None
    comparisons: list[dict[str, Any]]


class ProjectOverviewEntry(BaseModel):
    brand_id: int
    brand_name: str
    project_context: str
    competitor_count: int
    active_prompt_count: int
    run_count_30d: int
    high_risk_claim_count_30d: int
    hijack_count_30d: int
    mention_rate_last_run: float
    last_run_provider: RunProvider | None
    last_run_status: RunStatus | None
    last_run_started_at: datetime | None


class ProjectsOverviewResponse(BaseModel):
    total_projects: int
    healthy_projects: int
    warning_projects: int
    items: list[ProjectOverviewEntry]


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    org_id: int
    brand_id: int
    report_type: ReportType
    period_start: date
    period_end: date
    file_path: str
    created_at: datetime


class WeeklyReportRequest(BaseModel):
    week_start: date


class MonthlyReportRequest(BaseModel):
    month: str
