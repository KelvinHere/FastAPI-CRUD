# Create the tables for the TO-DO database

from sqlalchemy import Column, String, Boolean, Integer
from database import Base

class Item(Base):
    __tablename__= 'items'
    id = Column(Integer, primary_key=True)
    task = Column(String(128))
    completed = Column(Boolean(False))