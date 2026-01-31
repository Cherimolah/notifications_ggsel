import asyncio
import time
import hashlib
import datetime

from aiohttp import ClientSession

from models import LastSalesResponse, ProductsAllResponse, OrderInfoResponse, ProductInfoResponse

BASE_URL = "https://seller.ggsel.net"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://seller.ggsel.net/",
    "Origin": "https://seller.ggsel.net",
    'locale': 'ru',
    'lang': 'ru-RU'
}


class GGSel:
    def __init__(self, token: str, seller_id: int):
        self.base_token = token
        self.seller_id = seller_id
        self.token = None

    async def connect(self):
        ts = str(int(time.time()))
        sign = hashlib.sha256(f'{self.base_token}{ts}'.encode('utf-8')).hexdigest()
        payload = {
            "seller_id": self.seller_id,
            "timestamp": ts,
            "sign": sign
        }
        async with ClientSession() as session:
            response = await session.post(BASE_URL + '/api_sellers/api/apilogin', json=payload, headers=HEADERS)
            data = await response.json()
        self.token = data['token']
        valid_through = datetime.datetime.strptime(data['valid_thru'][:-2], '%Y-%m-%dT%H:%M:%S.%f').replace(
            tzinfo=datetime.timezone.utc)
        now = datetime.datetime.now(datetime.timezone.utc)
        timeout = (valid_through - now).total_seconds()
        asyncio.create_task(self.update_token(timeout=timeout))

    async def update_token(self, timeout: float):
        await asyncio.sleep(timeout)
        await self.connect()

    async def request(self, method: str, url: str, params: dict = None, data: dict = None) -> str:
        if not 'token' in params:
            params['token'] = self.token
        async with ClientSession() as session:
            response = await session.request(method, BASE_URL + url, params=params, json=data, headers=HEADERS)
            data = await response.text()
        return data

    async def get_all_products(self, ids: list[int] = None, page: int = 1, count: int = 10) -> ProductsAllResponse:
        # API Docs: https://seller.ggsel.net/docs/return-all-products
        url = '/api_sellers/api/products/list'
        if ids:
            ids = ','.join(map(str, ids))
        else:
            ids = ''
        params = {
            'ids': ids,
            'page': page,
            'count': count,
        }
        data = await self.request('GET', url, params)
        return ProductsAllResponse.model_validate_json(data)

    async def get_last_sales(self, group: bool = None, top: int = 10) -> LastSalesResponse:
        # API Docs: https://seller.ggsel.net/docs/return-last-sales
        url = '/api_sellers/api/seller-last-sales'
        params = {
            'top': top
        }
        if group is not None:
            params['group'] = group
        data = await self.request(method='GET', url=url, params=params)
        return LastSalesResponse.model_validate_json(data)

    async def get_order_info(self, invoice_id: int) -> OrderInfoResponse:
        # API Docs: https://seller.ggsel.net/docs/get-order-info
        url = f'/api_sellers/api/purchase/info/{invoice_id}'
        params = {}
        data = await self.request(method='GET', url=url, params=params)
        return OrderInfoResponse.model_validate_json(data)

    async def get_product_info(self, product_id: int) -> ProductInfoResponse:
        # API Docs: https://seller.ggsel.net/docs/return-product-info
        url = f'/api_sellers/api/products/{product_id}/data'
        params = {}
        data = await self.request(method='GET', url=url, params=params)
        return ProductInfoResponse.model_validate_json(data)

    async def get_all_categories(self, page: int = 1, count: int = 1, category_id: int = None):
        # API Docs: https://seller.ggsel.net/docs/return-all-categories

        # I don't know how "category_id" params work

        url = '/api_sellers/api/categories'
        params = {
            'page': page,
            'count': count
        }
        if category_id:
            params['category_id'] = category_id
        data = await self.request(method='GET', url=url, params=params)
        return data

    async def send_message(self, id_i: int, message: str):
        # API Docs: https://seller.ggsel.net/docs/create-message-without-file

        url = '/api_sellers/api/debates/v2'
        params = {
            'id_i': id_i
        }
        data = {
            'message': message
        }
        await self.request(method='POST', url=url, params=params, data=data)

