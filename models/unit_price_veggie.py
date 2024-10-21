from sqlalchemy import Column, Float,Integer, ForeignKey
from .veggie import Veggie

class UnitPriceVeggie(Veggie):
    __tablename__ = 'unit_price_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key=True)
    quantity = Column(Float, nullable=False)
    price_per_unit = Column(Float, nullable=False)

    def calculate_unit_price(self, quantity, price_per_unit):
        return quantity * price_per_unit
        

    def __repr__(self):
        return f"<UnitPriceVeggie(name={self.veg_name}, quantity={self.quantity})>"
