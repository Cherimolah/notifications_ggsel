import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.requests import Request
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


@app.route('/notification', methods=['POST', 'GET'])
async def notification_route(request: Request):
    await bot.send_message(ADMIN_ID,
                           'Афигеть! Какой-то кельпастник оплатил товар! Выдай ему\n\n'
                           f'{json.loads(await request.body())}')


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8003)
