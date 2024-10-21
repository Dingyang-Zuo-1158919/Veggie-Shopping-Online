from sqlalchemy import Column, Float,Integer, ForeignKey
from .veggie import Veggie

class PackVeggie(Veggie):
    __tablename__ = 'pack_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key=True)
    pack_quantity = Column(Float, nullable=False)
    price_per_pack = Column(Float, nullable=False)

    def calculate_pack_price(self, quantity, price_per_pack):
        return quantity * price_per_pack

    def __repr__(self):
        return f"<PackVeggie(name={self.veg_name}, quantity={self.pack_quantity})>"
