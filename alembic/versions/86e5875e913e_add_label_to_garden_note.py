"""add label to garden note

Revision ID: 86e5875e913e
Revises: a1fe6f9d36cc
Create Date: 2026-07-02 18:31:06.955398

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "86e5875e913e"
down_revision: str | None = "a1fe6f9d36cc"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    notelabel = sa.Enum("milestone", "pest", "note", "action", "harvest", name="notelabel")
    op.add_column(
        "gardennote",
        sa.Column(
            "label",
            notelabel,
            nullable=False,
            server_default="note",
        ),
    )


def downgrade() -> None:
    op.drop_column("gardennote", "label")
