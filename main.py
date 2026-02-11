import asyncio
from contextlib import asynccontextmanager
import re

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from aiogram import Dispatcher
from pydantic import BaseModel
from aiogram.filters.command import CommandStart
from aiogram.types import Message
import uvicorn

from config import ADMIN_ID
from database import connect
from utils import send_verification_code, send_message
from loader import bot, ggsel


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ggsel.connect()
    await connect()
    # asyncio.create_task(long_poll())
    yield

app = FastAPI(lifespan=lifespan)
dp = Dispatcher()
email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'


class Notification(BaseModel):
    id_i: int
    id_d: int
    amount: float
    currency: str
    email: str
    date: str
    ip: str
    SHA256: str
    is_my_product: bool


class Product(BaseModel):
    id: int
    cnt: float
    lang: str


class Option(BaseModel):
    id: int
    type: str
    value: str | int


class CheckParams(BaseModel):
    product: Product
    options: list[Option]



game_codes = {
    'clash of clans': 'magic',
    'clash royale': 'scroll',
    'brawl stars': 'laser'
}


@app.get('/')
async def index():
    return PlainTextResponse('welcome', status_code=200)


@app.post('/check')
async def check_order_params(check_params: CheckParams):
    item = await ggsel.get_product_info(check_params.product.id)
    reply = f'Хмммм, какой-то кельпастник собирается купить {item.product.name}'
    for option in check_params.options:
        if option.type == 'text':
            if not re.match(email_pattern, option.value):
                return PlainTextResponse('invalid email', status_code=400)
    asyncio.create_task(send_message(ADMIN_ID, reply))
    return PlainTextResponse('thx', status_code=200)


@app.post('/notification')
async def notification_route(notification: Notification):
    item = await ggsel.get_product_info(notification.id_d)
    reply = f'🛒 Афигеть! Какой-то кельпастник оплатил товар! Выдай ему\n\n'
    reply += (f'Товар: {item.product.name}\n'
              f'Стоимость: {item.product.price}\n\n')
    order = await ggsel.get_order_info(notification.id_i)
    reply += '⚙️ Параметры заказа:\n'
    email = None
    for option in order.content.options:
        reply += f'• {option.name}: {option.user_data}\n'
        if 'id' in option.name.lower():
            email = option.user_data
    asyncio.create_task(send_message(ADMIN_ID, reply))
    for game, code in game_codes.items():
        if game in item.product.name.lower():
            break
    else:
        raise Exception()
    asyncio.create_task(send_verification_code(email, game, notification.id_i))
    return PlainTextResponse('thx', status_code=200)


@dp.message(CommandStart())
async def command_start(m: Message):
    await m.answer('Привет! 👋\n'
                   'Я — твой персональный помощник для отслеживания покупок на GGsel.\n\n'
                   'Я буду своевременно присылать тебе уведомления о новых покупках, изменениях статуса заказов и другой важной информации с твоего аккаунта.')


async def long_poll():
    await dp.start_polling(bot)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8003)
