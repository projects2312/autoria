from sqlalchemy import Column, Float, DateTime
from sqlalchemy import String, Integer
from db.engine import Base

from datetime import datetime
from pytz import timezone

kyiv_tz = timezone("Europe/Kyiv")

class Auto(Base):
    __tablename__ = "auto"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True)
    title = Column(String(255))
    price_usd = Column(Float, nullable=True)
    odometer = Column(Integer, nullable=True)
    username = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    images_count = Column(Integer, nullable=True)
    car_number = Column(String, nullable=True)
    car_vin = Column(String, nullable=True)
    datetime_found = Column(DateTime, default=lambda: datetime.now(kyiv_tz))
