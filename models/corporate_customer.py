from models.customer import Customer
from sqlalchemy import Column, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

class CorporateCustomer(Customer):
    __tablename__ = 'corporate_customers'

    id = Column(Integer, ForeignKey('customers.id'), primary_key=True)

    discount_rate = Column(Float, default=0.1)
    max_credit = Column(Float, default=200.0)
    min_balance = Column(Float, default=1000.0)

    def __repr__(self):
        return f"<CorporateCustomer(username={self.username}, discount_rate={self.discount_rate})>"
