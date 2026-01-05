import os

from dotenv import load_dotenv


load_dotenv()


TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GGSEL_TOKEN = os.getenv("GGSEL_TOKEN")
SELLER_ID = int(os.getenv("SELLER_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

DB_HOST = os.getenv('DB_HOST')
DB_PORT = int(os.getenv('DB_PORT'))
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
