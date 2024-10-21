from sqlalchemy import Column, Integer, String
from .database import Base

class Person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(128), nullable=False)
    last_name = Column(String(128), nullable=False)
    password = Column(String(512), nullable=False)
    username = Column(String(128), unique=True, nullable=False)

    def __repr__(self):
        return f"<Person(username={self.username})>"