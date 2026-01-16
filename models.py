from sqlmodel import SQLModel, Field
from pydantic import FilePath

from utils import get_current_course


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True, nullable=True)
    name: str
    in_stock: str | None = None
    price_value: float | None = None
    price_currency: str | None = None
    image: FilePath | None = None

    @property
    def current_price(self) -> str:
        result = '---'
        if self.price_value and self.price_currency:
            result = round(self.price_value * get_current_course(self.price_currency), 2)
            result = str(result)
        return result
