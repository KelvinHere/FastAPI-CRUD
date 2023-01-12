from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine, SessionLocal
from enum import Enum
from typing import Union

from sqlalchemy.orm import Session

import tags as tags
import schemas as schemas
import models as models

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
app = FastAPI(
        openapi_tags=tags.tags_metadata,
        title="ToDo",
        description=tags.app_description
        )

origins = [
    "http://localhost:3000",
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    #allow_origins=origins,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

class SortOptions(str, Enum):
    NAME_ASC = "NAME_ASC"
    NAME_DESC = "NAME_DESC"
    IMPORTANCE_ASC = "IMPORTANCE_ASC"
    IMPORTANCE_DESC = "IMPORTANCE_DESC"


# Home shows all items in DB defaults sort to Task ascending
@app.get("/", tags=["home"])
def home(session: Session = Depends(get_session), q: Union[str, None] = None, sortBy: SortOptions = SortOptions.NAME_ASC, resultQty:int = -1):
    # Start query
    items = session.query(models.Item)

    # Add sort to query
    if sortBy == SortOptions.NAME_ASC:
        items = items.order_by(models.Item.task.asc())
    
    if sortBy == SortOptions.NAME_DESC:
        items = items.order_by(models.Item.task.desc())

    if sortBy == SortOptions.IMPORTANCE_ASC:
        items = items.order_by(models.Item.importance.asc())

    if sortBy == SortOptions.IMPORTANCE_DESC:
        items = items.order_by(models.Item.importance.desc())

    # number of results
    if resultQty != -1:
        items = items.limit(resultQty)

    # Add text filter or none to query
    if q:
        items = items.filter(models.Item.task.contains(q)).all()
    else:
        items = items.all()


    session.close()
    return items


# Get an individual item by ID
@app.get("/{id}", tags=["get_item"])
def get_item(id:int, session: Session = Depends(get_session)):
    item = session.query(models.Item).get(id)
    session.close()
    return item


# Create a new item using Item schema
@app.post("/", tags=["post_item"])
def add_item(item:schemas.Item, session: Session = Depends(get_session)):
    item = models.Item(task = item.task, completed = item.completed, importance = item.importance)
    session.add(item)
    session.commit()
    session.close()
    return item


# Update item by ID
@app.put("/{id}", tags=["update_item"])
def update_item(id:int, itemUpdated:schemas.Item, session: Session = Depends(get_session)):
    item = session.query(models.Item).get(id)
    item.task = itemUpdated.task
    item.completed = itemUpdated.completed
    item.importance = itemUpdated.importance
    session.commit()
    session.close()
    return item


# Delete item by ID
@app.delete("/{id}", tags=["delete_item"])
def delete_item(id:int, session: Session = Depends(get_session)):
    item = session.query(models.Item).get(id)
    session.delete(item)
    session.commit()
    session.close()
    return "Item deleted"