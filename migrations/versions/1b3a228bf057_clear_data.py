"""clear data

Revision ID: 1b3a228bf057
Revises: 04e7ba75a08a
Create Date: 2026-01-14 14:37:09.111585

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from models import Item


# revision identifiers, used by Alembic.
revision: str = '1b3a228bf057'
down_revision: Union[str, Sequence[str], None] = '04e7ba75a08a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sqlmodel.delete(Item))


def downgrade() -> None:
    """Downgrade schema."""
    pass
