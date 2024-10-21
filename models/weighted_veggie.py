from sqlalchemy import Column, Float,Integer, ForeignKey
from .veggie import Veggie

class WeightedVeggie(Veggie):
    __tablename__ = 'weighted_veggies'

    id = Column(Integer, ForeignKey('veggies.id'), primary_key=True)
    weight = Column(Float, nullable=False)
    weight_per_kilo = Column(Float, nullable=False)

    def calculate_weight_price(self, weight, weight_per_kilo):
        return weight * weight_per_kilo

    def __repr__(self):
        return f"<WeightedVeggie(name={self.veg_name}, weight={self.weight})>"
