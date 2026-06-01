"""Detección automática del ejecutivo

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-20

Cambios:
- calls.agent_id pasa a ser nullable (una llamada puede no estar asignada).
- Se añade calls.detected_agent_name (nombre detectado por la IA).
- Se añade calls.responsible (responsable de la subida del lote).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("calls", "agent_id", existing_type=sa.Integer(), nullable=True)
    op.add_column(
        "calls",
        sa.Column("detected_agent_name", sa.String(255), nullable=True),
    )
    op.add_column(
        "calls",
        sa.Column("responsible", sa.String(255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("calls", "responsible")
    op.drop_column("calls", "detected_agent_name")
    op.alter_column("calls", "agent_id", existing_type=sa.Integer(), nullable=False)
