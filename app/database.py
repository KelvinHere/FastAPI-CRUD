# Configuration of database for sqlAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Create DB type instance
engine = create_engine('sqlite:///todo.db', connect_args={"check_same_thread": False})

Base = declarative_base()

SessionLocal = sessionmaker(autocommit=False, bind=engine, expire_on_commit=False)
