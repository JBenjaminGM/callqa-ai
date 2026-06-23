"""Métricas de conversación por llamada

Revision ID: 0006
Revises: 0005
Create Date: 2026-06-23

Añade `calls.conversation_metrics` (JSON nullable) para guardar las métricas
deterministas de la conversación (talk-to-listen ratio, % de silencio, monólogo
más largo del agente, palabras/minuto, turnos/minuto). Las llamadas antiguas
quedan en NULL y se recalculan al vuelo desde la transcripción.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# JSONB en PostgreSQL, JSON genérico en el resto (coherente con los modelos).
_JSON = sa.JSON().with_variant(JSONB(), "postgresql")


def upgrade() -> None:
    op.add_column(
        "calls", sa.Column("conversation_metrics", _JSON, nullable=True)
    )


def downgrade() -> None:
    op.drop_column("calls", "conversation_metrics")
