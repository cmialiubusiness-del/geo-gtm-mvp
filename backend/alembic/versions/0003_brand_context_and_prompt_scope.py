"""Add brand context and brand-scoped prompt library."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_brand_ctx_prompt_scope"
down_revision = "0002_brand_scoped_projects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "brands",
        sa.Column("project_context", sa.String(length=255), nullable=False, server_default="通用行业"),
    )
    op.add_column("prompts", sa.Column("brand_id", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE prompts p
        SET brand_id = b.id
        FROM brands b
        WHERE b.org_id = p.org_id
          AND b.id = (
            SELECT id FROM brands b2 WHERE b2.org_id = p.org_id ORDER BY b2.id ASC LIMIT 1
          )
          AND p.brand_id IS NULL
        """
    )

    op.alter_column("prompts", "brand_id", nullable=False)
    op.create_foreign_key(
        "fk_prompts_brand_id_brands",
        "prompts",
        "brands",
        ["brand_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_prompts_brand_id", "prompts", ["brand_id"])


def downgrade() -> None:
    op.drop_index("ix_prompts_brand_id", table_name="prompts")
    op.drop_constraint("fk_prompts_brand_id_brands", "prompts", type_="foreignkey")
    op.drop_column("prompts", "brand_id")
    op.drop_column("brands", "project_context")
