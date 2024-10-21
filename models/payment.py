from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Payment(Base):
    __tablename__ = 'payments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))

    customer = relationship("Customer", back_populates="payments")
    corporate_customer = relationship("CorporateCustomer", back_populates="payments", overlaps="customer")
    order = relationship("Order", back_populates="payment")

    def __repr__(self):
        return f"<Payment(amount={self.payment_amount}, date={self.payment_date})>"
