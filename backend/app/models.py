from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
from app.db import Base


def enum_column(enum_cls: type, name: str) -> Enum:
    return Enum(enum_cls, name=name, native_enum=False)


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

    users: Mapped[list["User"]] = relationship(back_populates="organization")
    brands: Mapped[list["Brand"]] = relationship(back_populates="organization")
    competitors: Mapped[list["Competitor"]] = relationship(back_populates="organization")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="organization")
    runs: Mapped[list["Run"]] = relationship(back_populates="organization")
    snapshots: Mapped[list["MetricSnapshot"]] = relationship(back_populates="organization")
    reports: Mapped[list["Report"]] = relationship(back_populates="organization")


class User(Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("org_id", "email", name="uq_users_org_email"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(enum_column(UserRole, "user_role"), default=UserRole.admin)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped["Organization"] = relationship(back_populates="users")


class Brand(Base):
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSONB, default=list)
    project_context: Mapped[str] = mapped_column(String(255), nullable=False, default="通用行业")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped["Organization"] = relationship(back_populates="brands")
    competitors: Mapped[list["Competitor"]] = relationship(back_populates="brand")
    prompts: Mapped[list["Prompt"]] = relationship(back_populates="brand", overlaps="brand")
    runs: Mapped[list["Run"]] = relationship(back_populates="brand")
    reports: Mapped[list["Report"]] = relationship(back_populates="brand")


class Competitor(Base):
    __tablename__ = "competitors"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    aliases: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped["Organization"] = relationship(back_populates="competitors")
    brand: Mapped["Brand"] = relationship(back_populates="competitors")


class Prompt(Base):
    __tablename__ = "prompts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[PromptCategory] = mapped_column(
        enum_column(PromptCategory, "prompt_category"), nullable=False
    )
    intent_type: Mapped[PromptIntentType] = mapped_column(
        enum_column(PromptIntentType, "prompt_intent_type"), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    organization: Mapped["Organization"] = relationship(back_populates="prompts")
    brand: Mapped["Brand"] = relationship(back_populates="prompts", overlaps="prompts")
    answers: Mapped[list["Answer"]] = relationship(back_populates="prompt")


class Run(Base):
    __tablename__ = "runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), index=True)
    provider: Mapped[RunProvider] = mapped_column(enum_column(RunProvider, "run_provider"), index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[RunStatus] = mapped_column(
        enum_column(RunStatus, "run_status"), default=RunStatus.queued, index=True
    )

    organization: Mapped["Organization"] = relationship(back_populates="runs")
    brand: Mapped["Brand"] = relationship(back_populates="runs")
    answers: Mapped[list["Answer"]] = relationship(back_populates="run")
    snapshots: Mapped[list["MetricSnapshot"]] = relationship(back_populates="run")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), index=True)
    provider: Mapped[RunProvider] = mapped_column(enum_column(RunProvider, "answer_provider"))
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run: Mapped["Run"] = relationship(back_populates="answers")
    prompt: Mapped["Prompt"] = relationship(back_populates="answers")
    claims: Mapped[list["Claim"]] = relationship(back_populates="answer")
    hijacks: Mapped[list["Hijack"]] = relationship(back_populates="answer")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id", ondelete="CASCADE"), index=True)
    subject_type: Mapped[ClaimSubjectType] = mapped_column(
        enum_column(ClaimSubjectType, "claim_subject_type"), nullable=False, index=True
    )
    subject_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    claim_text: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[ClaimSentiment] = mapped_column(
        enum_column(ClaimSentiment, "claim_sentiment"), nullable=False, index=True
    )
    impact_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[ClaimRiskLevel] = mapped_column(
        enum_column(ClaimRiskLevel, "claim_risk_level"), nullable=False, index=True
    )
    is_factual_assertion: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    category: Mapped[PromptCategory] = mapped_column(
        enum_column(PromptCategory, "claim_category"), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    answer: Mapped["Answer"] = relationship(back_populates="claims")


class Hijack(Base):
    __tablename__ = "hijacks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id", ondelete="CASCADE"), index=True)
    prompt_id: Mapped[int] = mapped_column(ForeignKey("prompts.id", ondelete="CASCADE"), index=True)
    provider: Mapped[RunProvider] = mapped_column(enum_column(RunProvider, "hijack_provider"), index=True)
    hijack_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    hijack_strength: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    recommended_entities: Mapped[list[str]] = mapped_column(JSONB, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    answer: Mapped["Answer"] = relationship(back_populates="hijacks")


class MetricSnapshot(Base):
    __tablename__ = "metrics_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey("runs.id", ondelete="CASCADE"), index=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    jsonb_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    run: Mapped["Run"] = relationship(back_populates="snapshots")
    organization: Mapped["Organization"] = relationship(back_populates="snapshots")


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    org_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    brand_id: Mapped[int] = mapped_column(ForeignKey("brands.id", ondelete="CASCADE"), index=True)
    report_type: Mapped[ReportType] = mapped_column(
        enum_column(ReportType, "report_type"), nullable=False, index=True
    )
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

    organization: Mapped["Organization"] = relationship(back_populates="reports")
    brand: Mapped["Brand"] = relationship(back_populates="reports")
