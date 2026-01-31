from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator


class Product(BaseModel):
    """Модель продукта"""
    id: int
    name: Optional[str] = None
    price_rub: float = Field(alias="price_rub")
    price_usd: float = Field(alias="price_usd")
    price_eur: float = Field(alias="price_eur")
    price_uah: Optional[float] = None

    class Config:
        populate_by_name = True


class Sale(BaseModel):
    """Модель продажи"""
    invoice_id: int = Field(alias="invoice_id")
    date: datetime
    product: Product

    @field_validator('date', mode='before')
    @classmethod
    def parse_date(cls, value: str) -> datetime:
        """Парсинг даты из строки с часовым поясом"""
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    class Config:
        populate_by_name = True


class LastSalesResponse(BaseModel):
    """Основная модель ответа"""
    retval: int
    retdesc: str
    sales: List[Sale]
