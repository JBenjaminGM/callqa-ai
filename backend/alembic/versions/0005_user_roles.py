"""Roles de usuario y vínculo asesor-ejecutivo

Revision ID: 0005
Revises: 0004
Create Date: 2026-06-22

Añade users.agent_id (FK a agents) para vincular un asesor con su ficha de
ejecutivo, y migra el rol legacy 'supervisor' a 'jefe'.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("agent_id", sa.Integer(), nullable=True))
    op.create_index("ix_users_agent_id", "users", ["agent_id"])
    op.create_foreign_key(
        "fk_users_agent_id", "users", "agents", ["agent_id"], ["id"]
    )
    # El rol legacy 'supervisor' pasa a 'jefe' (mismos permisos de gestión).
    op.execute("UPDATE users SET role = 'jefe' WHERE role = 'supervisor'")


def downgrade() -> None:
    op.execute("UPDATE users SET role = 'supervisor' WHERE role IN ('jefe', 'admin')")
    op.drop_constraint("fk_users_agent_id", "users", type_="foreignkey")
    op.drop_index("ix_users_agent_id", table_name="users")
    op.drop_column("users", "agent_id")
