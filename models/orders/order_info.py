from datetime import datetime
from typing import List, Optional, Any, Literal
from enum import IntEnum

from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator


class InvoiceState(IntEnum):
    """Статусы инвойса"""
    CREATED = 1
    CANCELLED = 2
    PAID = 3
    COMPLETED = 4
    RETURNED = 5

class UniqueCodeStateInfo(BaseModel):
    """Информация о состоянии уникального кода"""
    state: Any
    date_check: Optional[datetime] = None
    date_delivery: Optional[datetime] = None
    date_confirmed: Optional[datetime] = None
    date_refuted: Optional[datetime] = None

    @field_validator('date_check', 'date_delivery', 'date_confirmed', 'date_refuted', mode='before')
    @classmethod
    def parse_optional_date(cls, value: Optional[str]) -> Optional[datetime]:
        """Парсинг опциональной даты"""
        if value is None:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))


class Option(BaseModel):
    """Опция товара/заказа"""
    id: int
    name: str
    user_data: Optional[str] = None
    user_data_id: Optional[int] = None


class BuyerInfo(BaseModel):
    """Информация о покупателе"""
    payment_method: str = Field(alias="payment_method")
    account: str
    email: str
    phone: Optional[str] = None
    skype: Optional[str] = None
    whatsapp: Optional[str] = None
    ip_address: Optional[str] = None
    payment_aggregator: str = Field(alias="payment_aggregator")

    class Config:
        populate_by_name = True


class Feedback(BaseModel):
    deleted: Optional[bool] = None
    feedback: Optional[str] = None
    feedback_type: Optional[Literal['positive', 'negative']] = None
    comment: Optional[str] = None



class Content(BaseModel):
    """Основной контент ответа"""
    item_id: int = Field(alias="item_id")
    content_id: int = Field(alias="content_id")
    cart_uid: Optional[str] = None
    name: str
    amount: float
    currency_type: str = Field(alias="currency_type")
    invoice_state: InvoiceState = Field(alias="invoice_state")
    purchase_date: datetime = Field(alias="purchase_date")
    date_pay: Optional[datetime] = Field(alias="date_pay", default=None)
    agent_id: Optional[int] = None
    agent_percent: Optional[float] = None
    agent_fee: float = Field(alias="agent_fee", default=0.0)
    query_string: Optional[str] = None
    unit_goods: Optional[str] = None
    cnt_goods: str = Field(alias="cnt_goods")
    promo_code: Optional[str] = None
    bonus_code: Optional[str] = None
    feedback: Optional[Feedback] = None
    unique_code_state: UniqueCodeStateInfo = Field(alias="unique_code_state")
    options: List[Option]
    buyer_info: BuyerInfo = Field(alias="buyer_info")
    owner: int
    day_lock: int = Field(alias="day_lock", ge=0)
    lock_state: str = Field(alias="lock_state")
    profit: float
    external_order_id: Optional[str] = None

    @field_validator('purchase_date', 'date_pay', mode='before')
    @classmethod
    def parse_date(cls, value: Optional[str]) -> Optional[datetime]:
        """Парсинг даты из строки с часовым поясом"""
        if value is None:
            return None
        return datetime.fromisoformat(value.replace("Z", "+00:00"))

    @field_validator('cnt_goods', mode='before')
    @classmethod
    def validate_cnt_goods(cls, value: Any) -> str:
        """Валидация поля cnt_goods - всегда возвращаем строку"""
        if value is None:
            return "0.0"
        return str(value)

    class Config:
        populate_by_name = True


class OrderInfoResponse(BaseModel):
    """Основная модель ответа с деталями инвойса"""
    retval: int = None
    retdesc: str = None
    content: Content = None
