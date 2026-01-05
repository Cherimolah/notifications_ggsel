from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from fastapi.requests import Request
from aiogram import Bot, Dispatcher
from pydantic import BaseModel
from aiogram.enums.parse_mode import ParseMode
from aiogram.filters.command import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import uvicorn

from config import TELEGRAM_TOKEN, GGSEL_TOKEN, ADMIN_ID
from ggsel import GGSel
from models import InvoiceState
from database import connect, Invoices, db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ggsel.connect()
    await connect()
    asyncio.create_task(poll_orders())
    asyncio.create_task(long_poll())
    yield

app = FastAPI(lifespan=lifespan)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
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
                           f'{await request.body()}')
    return PlainTextResponse('thx', status_code=200)


@dp.message(CommandStart())
async def command_start(m: Message):
    await m.answer('Привет! 👋\n'
                   'Я — твой персональный помощник для отслеживания покупок на GGsel.\n\n'
                   'Я буду своевременно присылать тебе уведомления о новых покупках, изменениях статуса заказов и другой важной информации с твоего аккаунта.')


async def poll_orders():
    sales = (await ggsel.get_last_sales(top=100)).sales
    invoice_ids = [x.invoice_id for x in sales]
    for invoice_id in invoice_ids:
        exist = await db.select([Invoices.id]).where(Invoices.invoice_id == invoice_id).gino.scalar()
        if not exist:
            order = await ggsel.get_order_info(invoice_id)
            await Invoices.create(invoice_id=invoice_id, status=order.content.invoice_state.value, item_id=order.content.item_id, sent=True)
    while True:
        sales = (await ggsel.get_last_sales(top=10)).sales
        invoice_ids = [x.invoice_id for x in sales]
        for invoice_id in invoice_ids:
            exist = await db.select([Invoices.id]).where(Invoices.invoice_id == invoice_id).gino.scalar()
            if not exist:
                order = await ggsel.get_order_info(invoice_id)
                await Invoices.create(invoice_id=invoice_id, status=order.content.invoice_state.value,
                                      item_id=order.content.item_id)
            else:
                sent = await db.select([Invoices.sent]).where(Invoices.invoice_id == invoice_id).gino.scalar()
                if sent:
                    continue
                order = await ggsel.get_order_info(invoice_id)
                if order.content.invoice_state.value < 3:
                    continue
            if order.content.invoice_state == InvoiceState.PAID:
                product = await ggsel.get_product_info(order.content.item_id)
                reply = (f'🛒 **НОВАЯ ПОКУПКА!** 🎉\n\n'
                         f'📦 **Товар:** {product.product.name})\n'
                         f'📋 **Заказ №:** {order.content.content_id}\n'
                         f'💰 **Сумма заказа:** {order.content.amount} ₽\n'
                         f'💳 **К выплате:** {order.content.profit} ₽\n'
                         f'👤 **Покупатель:** {order.content.buyer_info.account}\n'
                         f'📅 **Дата оплаты:** {order.content.date_pay}')
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[
                    InlineKeyboardButton(text='Ссылка на заказ', url=f'https://seller.ggsel.net/orders/{invoice_id}')
                ]])
                await bot.send_message(ADMIN_ID, reply, parse_mode=ParseMode.MARKDOWN, reply_markup=keyboard)
                await Invoices.update.values(sent=True).where(Invoices.invoice_id == invoice_id).gino.status()
        await asyncio.sleep(60)


async def long_poll():
    await dp.start_polling(bot)


if __name__ == '__main__':
    uvicorn.run(app, host="127.0.0.1", port=8003)
