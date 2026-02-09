import asyncio
import json
import random
from typing import Literal
from string import ascii_lowercase
import subprocess

from aiohttp import ClientSession, ClientTimeout
from aiohttp_proxy import ProxyConnector

from loader import bot
from config import USER_ID


game_ids = {
    'scroll': 9,
    'laser': 11,
    'magic': 8
}


headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Accept-Language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Host': 'api.nexus-shop.ru',
    'Origin': 'https://miniapp.nexus-shop.ru',
    'Pragma': 'no-cache',
    'Referer': 'https://miniapp.nexus-shop.ru/',
    'Sec-Ch-Ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Microsoft Edge";v="144", "Microsoft Edge WebView2";v="144"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': 'Windows',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0'
}


def create_connector():
    return ProxyConnector(
        host='127.0.0.1',
        port=9050,
        proto='socks5',
    )

async def send_message(chat_id: int, text: str):
    for _ in range(3):
        try:
            await bot.send_message(chat_id, text)
            return
        except:
            await asyncio.sleep(3)


async def send_verification_code(email: str, game: Literal['scroll', 'laser', 'magic']) -> bool:
    assert game in ('scroll', 'laser', 'magic')
    subprocess.run(['systemctl', 'restart', 'tor'])
    await asyncio.sleep(1)
    for _ in range(5):
        if 'Authorization' in headers:
            del headers['Authorization']
        user_id = random.randint(1, 100000000)
        data = {
            'userId': user_id,
            'fullName': ''.join(random.choices(ascii_lowercase, k=random.randint(4, 15))),
            'userName': ''.join(random.choices(ascii_lowercase, k=random.randint(4, 15))),
        }
        async with ClientSession(connector=create_connector()) as session:
            response = await session.post('https://api.nexus-shop.ru/api/appuser/login', headers=headers, json=data)
            data = await response.json()
        token = data['token']
        headers['Authorization'] = f'Bearer {token}'
        data = {"userId":user_id,"gameId":game_ids[game],"gameLink":email}
        await asyncio.sleep(3)
        async with ClientSession(connector=create_connector()) as session:
            await session.post('https://api.nexus-shop.ru/api/UserGameLink/add', headers=headers, json=data)
        await asyncio.sleep(10)
        url = 'https://api.nexus-shop.ru/api/Supercell/login'
        data = {
            'game': game,
            'email': email,
        }
        try:
            async with ClientSession(timeout=ClientTimeout(10), connector=create_connector()) as session:
                response = await session.post(url, headers=headers, json=data)
                data = await response.text()
            try:
                data = json.loads(data)
            except:
                await bot.send_message(USER_ID, f'Ошибка доставки кода {data}')
                await asyncio.sleep(3)
                continue
            if not data.get('ok') is True:
                await bot.send_message(USER_ID, f'Ошибка доставки кода {data}')
                await asyncio.sleep(3)
                continue
            else:
                await bot.send_message(USER_ID, 'Код успешно доставлен')
                return True
        except:
            continue
    return False
