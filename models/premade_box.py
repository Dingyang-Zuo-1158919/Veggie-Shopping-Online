from models.veggie import Veggie
from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .item import Item
from .database import Base

class PremadeBox(Item):
    __tablename__ = 'premade_boxes'

    id = Column(Integer, ForeignKey('items.id'), primary_key=True)
    box_size = Column(String(50), nullable=False)
    num_of_boxes = Column(Integer, nullable=False)

    # Establish a relationship to BoxContent
    box_contents = relationship("BoxContent", back_populates="premade_box")

    def calculate_box_price(self, box_size, quantity):
        # Calculate the box price by quantity and box size
        if box_size == 'small':
            price = float(12) * quantity
        elif box_size == 'medium':
            price = float(15) * quantity
        else:
            price = float(18) * quantity
        return price

    def __repr__(self):
        return f"<PremadeBox(size={self.box_size}, num_boxes={self.num_of_boxes})>"
    
class BoxContent(Base):
    __tablename__ = 'box_contents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    premade_box_id = Column(Integer, ForeignKey('premade_boxes.id'), nullable=False)
    box_content = Column(String(512), nullable=False)  # Name of the veggies

    # Establish a relationship back to PremadeBox
    premade_box = relationship("PremadeBox", back_populates="box_contents")

    def add_veggie(self, veggie):
        # Add a veggie name to the box_content list.
        current_content = self.box_content.split(',') if self.box_content else []
        current_content.append(veggie.veg_name)
        self.box_content = ','.join(current_content)

    def remove_veggie(self, veggie):
        # Remove a veggie name from the box_content list.
        if self.box_content:
            current_content = self.box_content.split(',')
            if veggie.veg_name in current_content:
                current_content.remove(veggie.veg_name)
                self.box_content = ','.join(current_content)