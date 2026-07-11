"""Corrige el server_default de users.role a 'jefe'

Revision ID: 0007
Revises: 0006
Create Date: 2026-07-11

La migración 0001 fijó `server_default='supervisor'` para `users.role`. El rol
'supervisor' quedó obsoleto (0005 lo migró a 'jefe' y ya no está en VALID_ROLES).
El ORM siempre pasa el rol explícito (default Python = 'jefe'), pero un INSERT SQL
directo sin rol insertaría un valor inválido. Se alinea el server_default con el
modelo.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=50),
        server_default="jefe",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=50),
        server_default="supervisor",
        existing_nullable=False,
    )
