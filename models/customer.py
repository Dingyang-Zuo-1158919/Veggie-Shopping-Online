from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from .person import Person

class Customer(Person):
    __tablename__ = 'customers'

    id = Column(Integer, ForeignKey('persons.id'), primary_key=True)

    cust_address = Column(String(512), nullable=False)
    cust_balance = Column(Float, default=100.0)
    max_owing = Column(Float, default=100.0)

    # Ensure this matches the relationship name used in Payment
    payments = relationship("Payment", back_populates="customer", cascade="all, delete-orphan")

    # Add this line to define the relationship with orders
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Customer(username={self.username}, balance={self.cust_balance})>"

    def customer_username(self):
        return self.username