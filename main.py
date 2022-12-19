from fastapi import FastAPI, Depends
import schemas
import models

from database import Base, engine, SessionLocal
from sqlalchemy.orm import Session

# Create database using the config created in database.py if not exists
Base.metadata.create_all(engine)

# Function creates/closes a session for the routes when called
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close

# Create FastApi app
app = FastAPI()

mockDB = {
    1:{'task':'Fix car', 'completed': False},
    2:{'task':'Clean loft', 'completed': False},
    3:{'task':'Learn FastAPI basics', 'completed': False}
}


# Home shows all items in DB
@app.get("/")
def home(session: Session = Depends(get_session)):
    items = session.query(models.Item).all()
    session.close()
    return items


# Get an individual item by ID
@app.get("/{id}")
def getItem(id:int, session: Session = Depends(get_session)):
    item = session.query(models.Item).get(id)
    session.close()
    return item


# Create a new item using Item schema
@app.post("/")
def addItem(item:schemas.Item, session: Session = Depends(get_session)):
    item = models.Item(task = item.task, completed = item.completed)
    session.add(item)
    session.commit()
    session.close()
    return item


# Update item by ID
@app.put("/{id}")
def updateItem(id:int, itemUpdated:schemas.Item, session: Session = Depends(get_session)):
    item = session.query(models.Item).get(id)
    item.task = itemUpdated.task
    item.completed = itemUpdated.completed
    session.commit()
    session.close()
    return item


# Delete item by ID
@app.delete("/{id}")
def updateItem(id:int, session: Session = Depends(get_session)):
    item = session.query(models.Item).get(id)
    session.delete(item)
    session.commit()
    session.close()
    return "Item deleted"