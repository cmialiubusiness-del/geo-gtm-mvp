"""Initial schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False, server_default="admin"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("org_id", "email", name="uq_users_org_email"),
    )
    op.create_index("ix_users_org_id", "users", ["org_id"])

    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_brands_org_id", "brands", ["org_id"])

    op.create_table(
        "competitors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "aliases",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_competitors_org_id", "competitors", ["org_id"])

    op.create_table(
        "prompts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("intent_type", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_prompts_org_id", "prompts", ["org_id"])

    op.create_table(
        "runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="queued"),
    )
    op.create_index("ix_runs_org_id", "runs", ["org_id"])
    op.create_index("ix_runs_provider", "runs", ["provider"])
    op.create_index("ix_runs_status", "runs", ["status"])
    op.create_index("ix_runs_started_at", "runs", ["started_at"])

    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prompt_id", sa.Integer(), sa.ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_answers_run_id", "answers", ["run_id"])
    op.create_index("ix_answers_prompt_id", "answers", ["prompt_id"])

    op.create_table(
        "claims",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("answer_id", sa.Integer(), sa.ForeignKey("answers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("subject_type", sa.String(length=32), nullable=False),
        sa.Column("subject_name", sa.String(length=255), nullable=False),
        sa.Column("claim_text", sa.Text(), nullable=False),
        sa.Column("sentiment", sa.String(length=8), nullable=False),
        sa.Column("impact_score", sa.Integer(), nullable=False),
        sa.Column("risk_level", sa.String(length=32), nullable=False),
        sa.Column("is_factual_assertion", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_claims_answer_id", "claims", ["answer_id"])
    op.create_index("ix_claims_subject_type", "claims", ["subject_type"])
    op.create_index("ix_claims_subject_name", "claims", ["subject_name"])
    op.create_index("ix_claims_sentiment", "claims", ["sentiment"])
    op.create_index("ix_claims_risk_level", "claims", ["risk_level"])
    op.create_index("ix_claims_category", "claims", ["category"])
    op.create_index("ix_claims_created_at", "claims", ["created_at"])

    op.create_table(
        "hijacks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("answer_id", sa.Integer(), sa.ForeignKey("answers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("prompt_id", sa.Integer(), sa.ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("provider", sa.String(length=32), nullable=False),
        sa.Column("hijack_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("hijack_strength", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "recommended_entities",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_hijacks_answer_id", "hijacks", ["answer_id"])
    op.create_index("ix_hijacks_prompt_id", "hijacks", ["prompt_id"])
    op.create_index("ix_hijacks_provider", "hijacks", ["provider"])
    op.create_index("ix_hijacks_hijack_flag", "hijacks", ["hijack_flag"])
    op.create_index("ix_hijacks_created_at", "hijacks", ["created_at"])

    op.create_table(
        "metrics_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("runs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("jsonb_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_metrics_snapshots_run_id", "metrics_snapshots", ["run_id"])
    op.create_index("ix_metrics_snapshots_org_id", "metrics_snapshots", ["org_id"])
    op.create_index("ix_metrics_snapshots_created_at", "metrics_snapshots", ["created_at"])

    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("org_id", sa.Integer(), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_type", sa.String(length=32), nullable=False),
        sa.Column("period_start", sa.Date(), nullable=False),
        sa.Column("period_end", sa.Date(), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_reports_org_id", "reports", ["org_id"])
    op.create_index("ix_reports_report_type", "reports", ["report_type"])
    op.create_index("ix_reports_created_at", "reports", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_reports_created_at", table_name="reports")
    op.drop_index("ix_reports_report_type", table_name="reports")
    op.drop_index("ix_reports_org_id", table_name="reports")
    op.drop_table("reports")

    op.drop_index("ix_metrics_snapshots_created_at", table_name="metrics_snapshots")
    op.drop_index("ix_metrics_snapshots_org_id", table_name="metrics_snapshots")
    op.drop_index("ix_metrics_snapshots_run_id", table_name="metrics_snapshots")
    op.drop_table("metrics_snapshots")

    op.drop_index("ix_hijacks_created_at", table_name="hijacks")
    op.drop_index("ix_hijacks_hijack_flag", table_name="hijacks")
    op.drop_index("ix_hijacks_provider", table_name="hijacks")
    op.drop_index("ix_hijacks_prompt_id", table_name="hijacks")
    op.drop_index("ix_hijacks_answer_id", table_name="hijacks")
    op.drop_table("hijacks")

    op.drop_index("ix_claims_created_at", table_name="claims")
    op.drop_index("ix_claims_category", table_name="claims")
    op.drop_index("ix_claims_risk_level", table_name="claims")
    op.drop_index("ix_claims_sentiment", table_name="claims")
    op.drop_index("ix_claims_subject_name", table_name="claims")
    op.drop_index("ix_claims_subject_type", table_name="claims")
    op.drop_index("ix_claims_answer_id", table_name="claims")
    op.drop_table("claims")

    op.drop_index("ix_answers_prompt_id", table_name="answers")
    op.drop_index("ix_answers_run_id", table_name="answers")
    op.drop_table("answers")

    op.drop_index("ix_runs_started_at", table_name="runs")
    op.drop_index("ix_runs_status", table_name="runs")
    op.drop_index("ix_runs_provider", table_name="runs")
    op.drop_index("ix_runs_org_id", table_name="runs")
    op.drop_table("runs")

    op.drop_index("ix_prompts_org_id", table_name="prompts")
    op.drop_table("prompts")

    op.drop_index("ix_competitors_org_id", table_name="competitors")
    op.drop_table("competitors")

    op.drop_index("ix_brands_org_id", table_name="brands")
    op.drop_table("brands")

    op.drop_index("ix_users_org_id", table_name="users")
    op.drop_table("users")

    op.drop_table("organizations")
