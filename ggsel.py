import asyncio
import time
import hashlib
import datetime

from aiohttp import ClientSession

from models import *

from config import SELLER_ID


BASE_URL = "https://seller.ggsel.net"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://seller.ggsel.net/",
    "Origin": "https://seller.ggsel.net",
    'locale': 'ru'
}


class GGSel:
    def __init__(self, token: str):
        self.base_token = token
        self.token = None

    async def connect(self):
        ts = str(int(time.time()))
        sign = hashlib.sha256(f'{self.base_token}{ts}'.encode('utf-8')).hexdigest()
        payload = {
            "seller_id": SELLER_ID,
            "timestamp": ts,
            "sign": sign
        }
        async with ClientSession() as session:
            response = await session.post(BASE_URL + '/api_sellers/api/apilogin', json=payload, headers=HEADERS)
            data = await response.json()
        self.token = data['token']
        valid_through = datetime.datetime.strptime(data['valid_thru'][:-2], '%Y-%m-%dT%H:%M:%S.%f').replace(tzinfo=datetime.timezone.utc)
        now = datetime.datetime.now(datetime.timezone.utc)
        timeout = (valid_through - now).total_seconds()
        asyncio.create_task(self.update_token(timeout=timeout))

    async def update_token(self, timeout: float):
        await asyncio.sleep(timeout)
        await self.connect()


    async def get_all_products(self, ids: list[int] = None, page: int = 1, count: int = 10) -> ProductsResponseModel:
        # API Docs: https://seller.ggsel.net/docs/return-all-products
        url = '/api_sellers/api/products/list'
        if ids:
            ids = ','.join(map(str, ids))
        else:
            ids = ''
        params = {
            'token': self.token,
            'ids': ids,
            'page': page,
            'count': count,
        }
        async with ClientSession() as session:
            response = await session.get(BASE_URL + url, params=params, headers=HEADERS)
            data = await response.text()
        return ProductsResponseModel.model_validate_json(data)
