import datetime

from gino import Gino
from sqlalchemy import Column, Integer, DateTime, BigInteger, Boolean

from config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


def now():
    return datetime.datetime.now(
        tz=datetime.timezone(datetime.timedelta(hours=3))
    )


db = Gino()


class Invoices(db.Model):
    __tablename__ = 'invoices'

    id = Column(Integer, primary_key=True)
    invoice_id = Column(BigInteger, unique=True)
    status = Column(Integer)
    item_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=now)
    sent = Column(Boolean, default=False)


async def connect():
    await db.set_bind(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    await db.gino.create_all()

