from sqlalchemy import Column, Integer
from sqlalchemy.orm import relationship
from .database import Base

class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # Relationship to refer back to OrderLine
    order_lines = relationship("OrderLine", back_populates="item")

    def __repr__(self):
        return "<Item>"
