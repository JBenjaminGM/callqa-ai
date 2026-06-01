"""Subcriterios de la rúbrica

Revision ID: 0003
Revises: 0002
Create Date: 2026-06-01

Añade rubric_config.criteria (JSON): subcategorías activables por dimensión,
con formato [{"name": str, "enabled": bool}].
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("rubric_config", sa.Column("criteria", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("rubric_config", "criteria")
