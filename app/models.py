# Create the tables for the TO-DO database

from sqlalchemy import Column, String, Boolean, Integer, DateTime, func
from database import Base

class Item(Base):
    __tablename__= 'items'
    id = Column(Integer, primary_key=True)
    task = Column(String(128), nullable=False)
    completed = Column(Boolean(False))
    created = Column(DateTime, default=func.now())
    importance = Column(Integer)