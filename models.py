from datetime import datetime
from typing import List, Optional, Union, Any, Literal, Dict
from enum import IntEnum

from pydantic import BaseModel, Field
from pydantic.functional_validators import field_validator


class SaleInfo(BaseModel):
    common_base_price: float
    common_price_usd: float
    common_price_rur: float
    common_price_eur: float
    sale_end: Optional[str] = None
    sale_percent: Optional[str] = None


class ProductRow(BaseModel):
    price: Union[float, str]
    currency: str
    cnt_sell: int
    cnt_return: int
    cnt_goodresponses: int
    cnt_badresponses: int
    price_usd: float
    price_rur: float
    price_eur: float
    price_uah: float
    in_stock: int
    num_in_stock: int
    visible: int
    commiss_agent: Optional[str] = None
    has_discount: Optional[str] = None
    num_options: int
    sale_info: SaleInfo
    id_goods: int
    name_goods: str
    info_goods: str
    add_info: str


class ProductsResponseModel(BaseModel):
    retval: int
    retdesc: str
    page: int
    count: int
    has_next_page: bool
    has_previous_page: bool
    total_count: int
    total_pages: int
    rows: List[ProductRow]


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


class SalesResponse(BaseModel):
    """Основная модель ответа"""
    retval: int
    retdesc: str
    sales: List[Sale]


class InvoiceState(IntEnum):
    """Статусы инвойса"""
    CREATED = 1
    CANCELLED = 2
    PAID = 3
    COMPLETED = 4
    RETURNED = 5

class UniqueCodeStateInfo(BaseModel):
    """Информация о состоянии уникального кода"""
    state: int
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


class OrderResponse(BaseModel):
    """Основная модель ответа с деталями инвойса"""
    retval: int = None
    retdesc: str = None
    content: Content = None


class PreviewImage(BaseModel):
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None

class PriceData(BaseModel):
    RUB: float = None
    USD: float = None
    EUR: float = None

class OptionVariant(BaseModel):
    value: int = None
    text: str = None
    default: int = None
    modify: str = None
    modify_type: str = None
    modify_value: str = None
    modify_value_default: str = None
    visible: int = None
    num_in_stock: int = None

class ProductOption(BaseModel):
    name: int = None
    label: str = None
    type: str = None
    separate_content: int = None
    required: int = None
    modifier_visible: int = None
    variants: List[OptionVariant]

class Breadcrumb(BaseModel):
    id: int = None
    name: str = None

class ProductStatistics(BaseModel):
    sales: int = None
    refunds: int = None
    good_reviews: int = None
    bad_reviews: int = None

class Seller(BaseModel):
    id: int = None
    name: str = None

class SaleInfoCommon(BaseModel):
    common_base_price: float = None
    common_price_usd: float = None
    common_price_rur: float = None
    common_price_eur: float = None
    sale_end: Optional[str] = None
    sale_percent: Optional[int] = None


class ProductFull(BaseModel):
    id: int = None
    id_prev: Optional[int] = None
    id_next: Optional[int] = None
    name: str = None
    price: float = None
    currency: str = None
    url: str = None
    info: str = None
    add_info: str = None
    release_date: str = None
    agency_fee: str = None
    agency_sum: Optional[float] = None
    agency_id: Optional[int] = None
    collection: str = None
    propertygood: int = None
    is_available: int = None
    show_rest: int = None
    num_in_lock: Optional[int] = None
    prices: Dict[str, PriceData] = None
    payment_methods: List[str] = None
    prices_unit: Optional[str] = None
    unique_code_verification: Optional[str] = None
    preview_imgs: List[PreviewImage]
    preview_videos: List[str]
    type: Optional[str] = None
    text: Optional[str] = None
    file: Optional[str] = None
    category_id: int = None
    breadcrumbs: List[Breadcrumb] = None
    discounts: Optional[Any] = None
    units: Optional[Any] = None
    present: Optional[Any] = None
    gift_commiss: Optional[Any] = None
    options: List[ProductOption]
    options_check: int = None
    statistics: ProductStatistics = None
    seller: Seller = None
    sale_info: SaleInfoCommon = None
    num_in_stock: int = None


class ProductResponse(BaseModel):
    retval: int
    retdesc: str
    product: ProductFull
