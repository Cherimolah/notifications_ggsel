import asyncio
import hmac
import base64
import urllib
import uuid
import time
import subprocess
from typing import Literal

import aiohttp
from aiohttp_socks import ProxyConnector

from loader import bot, ggsel
from config import CAPTCHA_TOKEN, ADMIN_ID, PROXY_IP, PROXY_PORT, PROXY_TYPE, PROXY_USER, PROXY_PASSWORD


games_data = {
    'magic': {
        'rfp_key': '64b9add2163812f8838e1588c544210f1a7044083f183aba0fba84d415c166b1',
        'site_key': '6LdAVCIqAAAAALFFhSHedUzchtFhnsJeucdWU_QN',
        'user-agent': 'scid/1.12.11 (Android 9; magic-prod; SM-S906N) com.supercell.clashofclans/18.0.10',
        'package_name': 'com.supercell.clashofclans'
    },
    'scroll': {
        'rfp_key': 'ca7088324e650669790965bded7a0e4bc8ef0384bf48791c9538443a9bf1485b',
        'site_key': '6LcxMCIqAAAAAIVTklRevyZkoCh3meCiSJDRTwc1',
        'user-agent': 'scid/1.12.11 (Android 9; scroll-prod; SM-S906N) com.supercell.clashroyale/130300033.130300033',
        'package_name': 'com.supercell.clashroyale'
    },
    'laser': {
        'rfp_key': 'ae584daf58a3757be21fb506dfcfc478fad4600e688d5bb6f3e51ccb2ebfc373',
        'site_key': '6LcBWxsqAAAAAJ4zUt4bdfgglSBdrW41BSQn-AIs',
        'user-agent': 'scid/1.12.16 (Android 9; laser-prod; SM-S906N) com.supercell.brawlstars/65.219.65219',
        'package_name': 'com.supercell.brawlstars'
    }
}


def sign(timestamp: int, path: str, method: str, body: str, headers: dict[str, str], game: str) -> str:
    key = bytes.fromhex(games_data[game]['rfp_key'])

    headers_str = ""
    headers_value_str = ""
    for header in ("Authorization", "User-Agent", "X-Supercell-Device-Id"):
        if header in headers:
            header_lower = header.lower()
            if len(headers_str) > 0:
                headers_str += ";"
            headers_str += header_lower
            headers_value_str += header_lower + "=" + headers[header]

    to_sign = f"{timestamp}{method}{path}{body}{headers_value_str}"
    x = hmac.digest(key, to_sign.encode("utf-8"), "sha256")
    xb = base64.b64encode(x).decode("utf-8").replace("+", "-").replace("/", "_").replace("=", "")
    return f"RFPv1 Timestamp={timestamp},SignedHeaders={headers_str},Signature={xb}"


async def solve_captcha(game: str) -> str:
    data = {
        "clientKey": CAPTCHA_TOKEN,
        "task": {
            "type": "RecaptchaMobileTask",
            "appPackageName": games_data[game]['package_name'],
            "appKey": games_data[game]['site_key'],
            "appAction": "BEGIN_CONNECT",
            "appDevice": "Android",
            'proxyType': PROXY_TYPE,
            'proxyAddress': PROXY_IP,
            'proxyPort': PROXY_PORT,
            'proxyLogin': PROXY_USER,
            'proxyPassword': PROXY_PASSWORD
        }
    }
    async with aiohttp.ClientSession() as session:
        response = await session.post("https://api.nextcaptcha.com/createTask", json=data)
        data = await response.json()
        task_id = data["taskId"]
    await asyncio.sleep(5)
    while True:
        data = {
            "clientKey": CAPTCHA_TOKEN,
            "taskId": task_id
        }
        async with aiohttp.ClientSession() as session:
            response = await session.post("https://api.nextcaptcha.com/getTaskResult", json=data)
            data = await response.json()
            if data['status'] != 'processing':
                token = data.get('solution').get('gRecaptchaResponse')
                break
            await asyncio.sleep(5)
    if not token:
        raise Exception("Failed to get captcha token")
    return token


async def send_message(chat_id: int, text: str):
    for _ in range(3):
        try:
            await bot.send_message(chat_id, text)
            return
        except:
            await asyncio.sleep(3)


async def send_verification_code(email: str, game: Literal['scroll', 'laser', 'magic'], id_i: int):
    assert game in ('scroll', 'laser', 'magic')
    try:
        solution = await solve_captcha(game)
    except:
        await ggsel.send_message(id_i,
                                 f'Здравствуйте! К сожалению, нам не удалось сформировать запрос на отправку кода :(\n'
                                 f'Подождите ответа продавца')
        await bot.send_message(ADMIN_ID, 'Капча не создана')
        return
    ts = int(time.time())
    host = "https://id.supercell.com"
    path = "/api/account/v2/pinAuthentication.start"
    body = urllib.parse.urlencode({
        'scope': 'account/connect',
        'identifier': email,
        'identifierType': 'EMAIL',
        'application': f'{game}-prod',
        'recaptchaToken': solution,
        'recaptchaSiteKey': games_data[game]['site_key'],
        'intent': 'LOGIN'
    })
    headers = {
        "User-Agent": games_data[game]['user-agent'],
        "Accept-Language": "ru",
        "Accept-Encoding": "gzip, deflate, br",
        'Content-Length': str(len(body)),
        'Host': 'id.supercell.com',
        "X-Supercell-Device-Id": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "Connection": 'keep-alive'
    }
    headers["X-Supercell-Request-Forgery-Protection"] = sign(ts, path, "POST", body, headers, game)
    # subprocess.run(['systemctl', 'restart', 'tor'])
    # await asyncio.sleep(1)
    # connector = ProxyConnector.from_url('socks5://127.0.0.1:9050')
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{host}{path}", headers={k.lower(): v for k, v in headers.items()},
                                data=body) as response:
            data = await response.json()
    if data.get('ok') is True:
        await ggsel.send_message(id_i,
                           f'Здравствуйте! На указанную вами почту «{email}» автоматически был отправлен код для входа в игру.\n'
                           f'Отправьте его в чат, в ближайшее время оператор зайдет в аккаунт и доставит товар.\n'
                           f'Если код не пришел, напишите в чате, отправим вручную повторно')
        await bot.send_message(ADMIN_ID, 'Код успешно отправлен')
    else:
        await ggsel.send_message(id_i,
                                 f'Здравствуйте! К сожалению, нам не удалось сформировать запрос на отправку кода :(\n'
                                 f'Подождите ответа продавца')
        await bot.send_message(ADMIN_ID, 'Суперы забраковали')
