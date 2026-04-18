"""adding label field to note

Revision ID: 5672d9a5144c
Revises: 196c64662ef9
Create Date: 2026-04-09 20:01:30.220871

"""
from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op


# revision identifiers, used by Alembic.
revision: str = '5672d9a5144c'
down_revision: str | None = '196c64662ef9'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    notelabel = sa.Enum('milestone', 'pest', 'note', 'action', name='notelabel')
    notelabel.create(op.get_bind())
    op.add_column('note', sa.Column(
        'label',
        notelabel,
        nullable=False,
        server_default='note',
    ))


def downgrade() -> None:
    op.drop_column('note', 'label')
    sa.Enum(name='notelabel').drop(op.get_bind())
