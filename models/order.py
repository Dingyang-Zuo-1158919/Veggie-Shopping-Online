from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship
from models.database import Base

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_date = Column(Date, nullable=False)
    order_number = Column(Integer, nullable=False)
    order_status = Column(String(50), nullable=False)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    staff_id = Column(Integer, ForeignKey('staffs.id'))
    payment_id = Column(Integer, ForeignKey('payments.id'))

    customer = relationship("Customer", back_populates="orders")
    staff = relationship("Staff", back_populates="orders")
    order_lines = relationship("OrderLine", back_populates="order")
    payment = relationship("Payment", back_populates="order")

    def __repr__(self):
        return f"<Order(order_number={self.order_number}, status={self.order_status})>"
