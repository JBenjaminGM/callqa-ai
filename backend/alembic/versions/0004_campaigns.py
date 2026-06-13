"""Campañas con nota de producto

Revision ID: 0004
Revises: 0003
Create Date: 2026-06-13

Crea la tabla `campaigns` (entidad de campaña con su nota de producto) y añade
`calls.campaign_id` (FK nullable). Hace un backfill: convierte los nombres de
campaña ya existentes (en `calls.campaign_type` y `agents.campaign`) en filas de
`campaigns` y enlaza las llamadas por nombre.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("product_service", sa.String(200), nullable=True),
        sa.Column("offer_description", sa.Text(), nullable=True),
        sa.Column("key_benefits", sa.JSON(), nullable=True),
        sa.Column("pricing_conditions", sa.Text(), nullable=True),
        sa.Column("customer_requirements", sa.Text(), nullable=True),
        sa.Column("mandatory_phrases", sa.JSON(), nullable=True),
        sa.Column("prohibited_claims", sa.JSON(), nullable=True),
        sa.Column("target_audience", sa.String(300), nullable=True),
        sa.Column("additional_notes", sa.Text(), nullable=True),
        sa.Column("source", sa.String(20), nullable=False, server_default="form"),
        sa.Column("source_filename", sa.String(255), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index("ix_campaigns_name", "campaigns", ["name"], unique=True)

    op.add_column("calls", sa.Column("campaign_id", sa.Integer(), nullable=True))
    op.create_index("ix_calls_campaign_id", "calls", ["campaign_id"])
    op.create_foreign_key(
        "fk_calls_campaign_id", "calls", "campaigns", ["campaign_id"], ["id"]
    )

    # --- Backfill: crea campañas a partir de los nombres ya usados ---
    conn = op.get_bind()
    conn.execute(
        sa.text(
            """
            INSERT INTO campaigns (name, source, active, created_at, updated_at)
            SELECT DISTINCT campaign_type, 'migrated', true, now(), now()
            FROM calls
            WHERE campaign_type IS NOT NULL AND campaign_type <> ''
              AND campaign_type NOT IN (SELECT name FROM campaigns)
            """
        )
    )
    conn.execute(
        sa.text(
            """
            INSERT INTO campaigns (name, source, active, created_at, updated_at)
            SELECT DISTINCT campaign, 'migrated', true, now(), now()
            FROM agents
            WHERE campaign IS NOT NULL AND campaign <> ''
              AND campaign NOT IN (SELECT name FROM campaigns)
            """
        )
    )
    conn.execute(
        sa.text(
            """
            UPDATE calls
            SET campaign_id = c.id
            FROM campaigns c
            WHERE calls.campaign_type = c.name AND calls.campaign_id IS NULL
            """
        )
    )


def downgrade() -> None:
    op.drop_constraint("fk_calls_campaign_id", "calls", type_="foreignkey")
    op.drop_index("ix_calls_campaign_id", table_name="calls")
    op.drop_column("calls", "campaign_id")
    op.drop_index("ix_campaigns_name", table_name="campaigns")
    op.drop_table("campaigns")
