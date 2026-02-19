"""Add search indexes to memos table

Revision ID: b2c3d4e5f6g7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-19 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6g7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes for search performance."""
    # Add index on title for search
    op.create_index(op.f('ix_memos_title'), 'memos', ['title'], unique=False)
    # Add index on author for ownership queries
    op.create_index(op.f('ix_memos_author'), 'memos', ['author'], unique=False)


def downgrade() -> None:
    """Remove search indexes."""
    op.drop_index(op.f('ix_memos_author'), table_name='memos')
    op.drop_index(op.f('ix_memos_title'), table_name='memos')
