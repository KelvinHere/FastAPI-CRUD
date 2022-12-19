from fastapi import FastAPI
import schemas

app = FastAPI()

mockDB = {
    1:{'task':'Fix car', 'completed': False},
    2:{'task':'Clean loft', 'completed': False},
    3:{'task':'Learn FastAPI basics', 'completed': False}
}


# Home shows all items in DB
@app.get("/")
def home():
    return mockDB


# Get an individual item by ID
@app.get("/{id}")
def getItem(id:int):
    return mockDB[id]


# Create a new item using Item schema
@app.post("/")
def addItem(item:schemas.Item):
    newId = len(mockDB) + 1
    mockDB[newId] = {
        'task': item.task,
        'completed': item.completed
        }
    return mockDB


# Update item by ID
@app.put("/{id}")
def updateItem(id:int, item:schemas.Item):
    mockDB[id]['task'] = item.task
    mockDB[id]['completed'] = item.completed
    return mockDB


# Delete item by ID
@app.delete("/{id}")
def updateItem(id:int):
    mockDB.pop(id)
    return mockDB