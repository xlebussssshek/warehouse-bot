from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Stock(Base):
    __tablename__ = "stock"

    artikul = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Stock(artikul={self.artikul}, name={self.name}, quantity={self.quantity})>"