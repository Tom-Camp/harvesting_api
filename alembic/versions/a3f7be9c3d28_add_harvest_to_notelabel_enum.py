"""add harvest to notelabel enum

Revision ID: a3f7be9c3d28
Revises: 1c058908b8af
Create Date: 2026-05-27 06:56:23.221514

"""
from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a3f7be9c3d28'
down_revision: str | None = '1c058908b8af'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(sa.text("COMMIT"))
    connection.execute(sa.text("ALTER TYPE notelabel ADD VALUE IF NOT EXISTS 'harvest'"))


def downgrade() -> None:
    # PostgreSQL does not support removing values from a native enum type.
    pass
