import os

from dotenv import load_dotenv


load_dotenv()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GGSEL_TOKEN = os.getenv("GGSEL_TOKEN")
SELLER_ID = int(os.getenv("SELLER_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))