"""Acuse de recibo del asesor

Crea la tabla `acknowledgements`: lo que el asesor responde a la evaluación de
una de sus llamadas. Puede darla por leída, explicarse y pedir que su jefe la
revise; el jefe contesta en el mismo registro. Sin esto la evaluación es un
monólogo y el ciclo de coaching nunca se cierra.

Revision ID: 0010
Revises: 0009
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: Union[str, None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "acknowledgements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "call_id",
            sa.Integer(),
            sa.ForeignKey("calls.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column(
            "review_requested",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("manager_reply", sa.Text(), nullable=True),
        sa.Column(
            "replied_by",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("replied_at", sa.DateTime(), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.func.now(), nullable=True
        ),
        sa.Column(
            "updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=True
        ),
    )
    op.create_index("ix_acknowledgements_user_id", "acknowledgements", ["user_id"])
    # Se filtra por esta columna para listar las peticiones abiertas.
    op.create_index(
        "ix_acknowledgements_review_requested",
        "acknowledgements",
        ["review_requested"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_acknowledgements_review_requested", table_name="acknowledgements"
    )
    op.drop_index("ix_acknowledgements_user_id", table_name="acknowledgements")
    op.drop_table("acknowledgements")
