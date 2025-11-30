from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from aiogram import Bot
from pydantic import BaseModel
import uvicorn

from config import TELEGRAM_TOKEN, GGSEL_TOKEN, ADMIN_ID
from ggsel import GGSel



@asynccontextmanager
async def lifespan(app: FastAPI):
    await ggsel.connect()
    yield

app = FastAPI(lifespan=lifespan)
bot = Bot(token=TELEGRAM_TOKEN)
ggsel = GGSel(GGSEL_TOKEN)



class Notification(BaseModel):
    ID_I: int
    ID_D: int
    Amount: int
    Currency: str
    email: str
    Date: str
    SHA256: str
    ISMYPRODUCT: bool


@app.get('/')
async def index():
    return PlainTextResponse('welcome', status_code=200)


@app.post('/notification')
async def notification_route(notification: Notification):
    products = await ggsel.get_all_products()
    for product in products.rows:
        if notification.ID_D == product.id_goods:
            await bot.send_message(ADMIN_ID, f'Афигеть! Какой-то кельпастник купил {product.name_goods}!\n'
                                             f'Выдай ему товар\n'
                                             f'Дополнительная информация: {notification}')
            return PlainTextResponse('ok', status_code=200)
    return PlainTextResponse('who are you?', status_code=403)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8003)
