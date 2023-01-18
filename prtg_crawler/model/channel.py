from sqlalchemy import Column, String, JSON, DATETIME, TEXT, Integer, TIMESTAMP, DateTime, text
from . import Base
from sqlalchemy.sql import func


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    sensor_id = Column(Integer(), nullable=False)
    lastvalue = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
