from sqlalchemy import Column, String, Integer, DateTime, BigInteger
from sqlalchemy.sql import func
from .base import Base
from datetime import datetime

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True)
    artikul = Column(String, nullable=False)
    type = Column(String, nullable=False)
    quantity = Column(Integer)
    old_quantity = Column(Integer)
    new_quantity = Column(Integer)
    user_id = Column(BigInteger, nullable=False)
    details = Column(String)
    timestamp = Column(DateTime, server_default=func.now())