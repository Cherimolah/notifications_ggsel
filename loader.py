from aiogram import Bot
from ggsel import GGSel

from config import TELEGRAM_TOKEN, GGSEL_TOKEN, SELLER_ID


bot = Bot(token=TELEGRAM_TOKEN)
ggsel = GGSel(GGSEL_TOKEN, SELLER_ID)
