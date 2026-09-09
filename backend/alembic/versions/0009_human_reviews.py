"""Revisión humana de las notas (calibración)

Crea la tabla `reviews`: la puntuación que da una persona a una llamada,
guardada **junto a** la de la IA en lugar de sobrescribirla. Tener las dos
notas es lo que permite medir el acuerdo entre IA y humano, que es de lo que
trata calibrar.

Revision ID: 0009
Revises: 0008
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009"
down_revision: Union[str, None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# JSONB en PostgreSQL, JSON genérico en el resto (igual que el resto de modelos).
JSON_TYPE = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def upgrade() -> None:
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "call_id",
            sa.Integer(),
            sa.ForeignKey("calls.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "reviewer_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("global_score", sa.Integer(), nullable=False),
        sa.Column("dimension_scores", JSON_TYPE, nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "blind",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True
        ),
        sa.CheckConstraint(
            "global_score >= 0 AND global_score <= 100", name="ck_review_global_score"
        ),
    )
    op.create_index("ix_reviews_reviewer_id", "reviews", ["reviewer_id"])


def downgrade() -> None:
    op.drop_index("ix_reviews_reviewer_id", table_name="reviews")
    op.drop_table("reviews")
