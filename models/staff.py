from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .person import Person
from .database import Base

class Staff(Person):
    __tablename__ = 'staffs'

    id = Column(Integer, ForeignKey('persons.id'), primary_key=True)
    date_joined = Column(String(128), nullable=False)
    dept_name = Column(String(128), nullable=False)

    orders = relationship("Order", back_populates="staff", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Staff(username={self.username}, dept={self.dept_name})>"
