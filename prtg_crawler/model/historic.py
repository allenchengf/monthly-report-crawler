from sqlalchemy import Column, String, JSON, DATETIME, TEXT, Integer, TIMESTAMP, DateTime, text
from . import Base
from sqlalchemy.sql import func


class Historic(Base):
    __tablename__ = 'historic'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_id = Column(Integer(), nullable=False)
    channel_name = Column(String(255), nullable=False)
    prefix = Column(String(255), nullable=False)
    reserve_prefix = Column(String(255), nullable=True)
    incoming = Column(String(50), nullable=True)
    outgoing = Column(String(50), nullable=True)
    raw_incoming = Column(String(50), nullable=True)
    raw_outgoing = Column(String(50), nullable=True)
    datetime = Column(TIMESTAMP, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


  # `sensor_id` int(11) NOT NULL,
  # `channel_name` varchar(255) DEFAULT NULL,
  # `prefix` varchar(255) NOT NULL,
  # `reserve_prefix` varchar(255) DEFAULT NULL,
  # `incoming` varchar(50) DEFAULT NULL,
  # `outgoing` varchar(50) DEFAULT NULL,
  # `datetime` timestamp NULL DEFAULT NULL,
  # `created_at` timestamp NULL DEFAULT NULL,
  # `updated_at` timestamp NULL DEFAULT NULL,