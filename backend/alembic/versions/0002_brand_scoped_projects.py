"""Brand-scoped project support."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_brand_scoped_projects"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("competitors", sa.Column("brand_id", sa.Integer(), nullable=True))
    op.add_column("runs", sa.Column("brand_id", sa.Integer(), nullable=True))
    op.add_column("reports", sa.Column("brand_id", sa.Integer(), nullable=True))

    op.execute(
        """
        UPDATE competitors c
        SET brand_id = b.id
        FROM brands b
        WHERE b.org_id = c.org_id
          AND b.id = (
            SELECT id FROM brands b2 WHERE b2.org_id = c.org_id ORDER BY b2.id ASC LIMIT 1
          )
          AND c.brand_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE runs r
        SET brand_id = b.id
        FROM brands b
        WHERE b.org_id = r.org_id
          AND b.id = (
            SELECT id FROM brands b2 WHERE b2.org_id = r.org_id ORDER BY b2.id ASC LIMIT 1
          )
          AND r.brand_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE reports r
        SET brand_id = b.id
        FROM brands b
        WHERE b.org_id = r.org_id
          AND b.id = (
            SELECT id FROM brands b2 WHERE b2.org_id = r.org_id ORDER BY b2.id ASC LIMIT 1
          )
          AND r.brand_id IS NULL
        """
    )

    op.alter_column("competitors", "brand_id", nullable=False)
    op.alter_column("runs", "brand_id", nullable=False)
    op.alter_column("reports", "brand_id", nullable=False)

    op.create_foreign_key(
        "fk_competitors_brand_id_brands",
        "competitors",
        "brands",
        ["brand_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_runs_brand_id_brands",
        "runs",
        "brands",
        ["brand_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "fk_reports_brand_id_brands",
        "reports",
        "brands",
        ["brand_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index("ix_competitors_brand_id", "competitors", ["brand_id"])
    op.create_index("ix_runs_brand_id", "runs", ["brand_id"])
    op.create_index("ix_reports_brand_id", "reports", ["brand_id"])


def downgrade() -> None:
    op.drop_index("ix_reports_brand_id", table_name="reports")
    op.drop_index("ix_runs_brand_id", table_name="runs")
    op.drop_index("ix_competitors_brand_id", table_name="competitors")

    op.drop_constraint("fk_reports_brand_id_brands", "reports", type_="foreignkey")
    op.drop_constraint("fk_runs_brand_id_brands", "runs", type_="foreignkey")
    op.drop_constraint("fk_competitors_brand_id_brands", "competitors", type_="foreignkey")

    op.drop_column("reports", "brand_id")
    op.drop_column("runs", "brand_id")
    op.drop_column("competitors", "brand_id")
