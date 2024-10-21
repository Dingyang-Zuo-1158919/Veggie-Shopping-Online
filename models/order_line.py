from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .database import Base

class OrderLine(Base):
    __tablename__ = 'order_lines'

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_number = Column(Integer, nullable=False)
    order_id = Column(Integer, ForeignKey('orders.id'))
    an_item_id = Column(Integer, ForeignKey('items.id'))
    # for 'BoxContent' when dealing with 'PremadeBox'
    box_content_id = Column(Integer, ForeignKey('box_contents.id'), nullable=True)

    item_type = Column(String(50), nullable=False)

    order = relationship("Order", back_populates="order_lines")
    item = relationship("Item", back_populates="order_lines")
    box_content = relationship("BoxContent", foreign_keys=[box_content_id])  # Link to BoxContent for PremadeBox

    def __repr__(self):
        return f"<OrderLine(item_number={self.item_number})>"
