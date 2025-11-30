from typing import List, Optional, Union

from pydantic import BaseModel

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
