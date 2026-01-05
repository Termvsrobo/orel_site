"""data migration

Revision ID: 526795e416dd
Revises: c84f9a755066
Create Date: 2025-12-31 17:47:41.054216

"""
import json
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

from models import Item


# revision identifiers, used by Alembic.
revision: str = '526795e416dd'
down_revision: Union[str, Sequence[str], None] = 'c84f9a755066'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    data = json.load(open("data.json", "r"))
    items = []
    for item in data:
        price_value = None
        if item["price_value"]:
            price_value = item["price_value"].replace(".", "").replace(",", ".")
            price_value = float(price_value)
        new_item = Item(
            name=item["name"],
            in_stock=item["in_stock"],
            price_value=price_value,
            price_currency=item["price_currency"],
        )
        items.append(new_item.model_dump(exclude=['id']))
    stmt = sqlmodel.insert(Item).values(items)
    op.execute(stmt)


def downgrade() -> None:
    """Downgrade schema."""
    pass
