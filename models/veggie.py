from sqlalchemy import Column, String, ForeignKey,Integer
from .item import Item
from .database import Base

class Veggie(Item):
    __tablename__ = 'veggies'

    id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    veg_name = Column(String(50), nullable=False)
    
    def __repr__(self):
        return f"<Veggie(name={self.veg_name})>"
