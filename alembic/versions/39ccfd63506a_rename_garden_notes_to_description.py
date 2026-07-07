"""rename garden notes to description

Revision ID: 39ccfd63506a
Revises: a3f7be9c3d28
Create Date: 2026-07-01 17:35:45.012400

"""
from collections.abc import Sequence

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '39ccfd63506a'
down_revision: str | None = 'a3f7be9c3d28'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column('garden', 'notes', new_column_name='description')


def downgrade() -> None:
    op.alter_column('garden', 'description', new_column_name='notes')
