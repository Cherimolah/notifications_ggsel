from typing import List, Optional, Any, Dict

from pydantic import BaseModel


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


class ProductInfoResponse(BaseModel):
    retval: int
    retdesc: str
    product: ProductFull
