from sqlalchemy import Column, String, JSON, DATETIME, TEXT, Integer, TIMESTAMP, DateTime, text
from . import Base
from sqlalchemy.sql import func


class Sensor(Base):
    __tablename__ = 'sensors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sensor_id = Column(Integer(), nullable=False)
    url = Column(String(255), nullable=True)
    tags = Column(String(255), nullable=True)
    status = Column(String(50), nullable=True)
    active = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
