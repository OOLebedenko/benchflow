"""add user role

Revision ID: b72457666c8d
Revises: 4d2cef98bcd0
Create Date: 2026-09-21 16:49:47.993479

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b72457666c8d"
down_revision: str | Sequence[str] | None = "4d2cef98bcd0"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
            server_default="user",
        ),
    )

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "users",
        "role",
    )
