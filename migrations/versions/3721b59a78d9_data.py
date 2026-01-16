"""data

Revision ID: 3721b59a78d9
Revises: 1b3a228bf057
Create Date: 2026-01-16 20:16:29.371123

"""
import json
import zipfile
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from models import Item


# revision identifiers, used by Alembic.
revision: str = '3721b59a78d9'
down_revision: Union[str, Sequence[str], None] = '1b3a228bf057'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    data_path = Path(__file__).parent / 'data' / 'item.json'
    with data_path.open() as f:
        data = json.load(f)
    with zipfile.ZipFile(data_path.parent / 'media.zip') as zf:
        zf.extractall(Path(__file__).parent.parent.parent)
    stmt = sqlmodel.insert(Item).values(data['item'])
    op.execute(stmt)


def downgrade() -> None:
    """Downgrade schema."""
    pass
