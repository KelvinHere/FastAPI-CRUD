from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import json

from main import app, get_session
from database import Base


# Create a test db
engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, bind=engine, expire_on_commit=False)
Base.metadata.create_all(bind=engine)


def override_get_session():
    try:
        session = TestingSessionLocal()
        yield session
    finally:
        session.close

# Change app dependency to new test DB
app.dependency_overrides[get_session] = override_get_session


client = TestClient(app)

# Add these to database before each test
fixture_1 = '''INSERT INTO items (task, importance, completed, 'created') VALUES ('Clean Loft', 2, true, '2022-12-21 12:30:01')'''
fixture_2 = '''INSERT INTO items (task, importance, completed, 'created') VALUES ('Fix Brakes', 10, false, '2022-12-21 12:35:01')'''
fixture_3 = '''INSERT INTO items (task, importance, completed, 'created') VALUES ('Buy Flour', 1, false, '2022-12-21 16:33:31')'''

# Expected responses
expected_fixture_1 = {'completed': True, 'importance': 2, 'id': 1, 'task': 'Clean Loft', 'created': '2022-12-21T12:30:01'}
expected_fixture_2 = {'completed': False, 'importance': 10, 'id': 2, 'task': 'Fix Brakes', 'created': '2022-12-21T12:35:01'}
expected_fixture_3 = {'completed': False, 'importance': 1, 'id': 3, 'task': 'Buy Flour', 'created': '2022-12-21T16:33:31'}
expected_added_task = {'completed': False, 'importance': 4, 'id': 4, 'task': 'Go Fishing', 'created': '2022-12-22T10:42:10'}
expected_fixture_1_after_update = {'completed': False, 'importance': 9, 'id': 1, 'task': 'Clean Loft Updated', 'created': '2022-12-21T12:30:01'}

# Items added through POSTing in tests
added_task = {'completed': False, 'importance': 4, 'task': 'Go Fishing'}
fixture_1_update = {'completed': False, 'importance': 9, 'task': 'Clean Loft Updated'}

############################################################# ADD & TEST FIXTURES

@pytest.fixture(autouse=True)
def setup_db() :
    Base.metadata.create_all(bind=engine)
    engine.execute(fixture_1)
    engine.execute(fixture_2)
    engine.execute(fixture_3)
    yield
    Base.metadata.drop_all(bind=engine)

def test_db_fixtures_loaded():
    response = client.get("/")
    data = response.json()
    assert expected_fixture_1 in data
    assert expected_fixture_2 in data
    assert expected_fixture_3 in data

############################################################# CRUD FEATURES

def test_add_task():
    #Tests adding a task to the database
    response = client.post("/", json=added_task)
    data = response.json()
    assert response.status_code == 200
    assert data['task'] == added_task['task']
    assert data['importance'] == added_task['importance']
    assert data['completed'] == added_task['completed']

def test_get_task_by_id():
    #Tests getting a task by specific ID
    response = client.get("/2")
    data = response.json()
    assert expected_fixture_2 == data

def test_delete_task():
    #Check task exists
    idForTest = 2
    response = client.get(f"/{idForTest}")
    data = response.json()
    assert expected_fixture_2 == data

    #Test task is deleted
    response = client.delete(f"/{idForTest}")
    assert response.status_code == 200
    assert response.json() == "Item deleted"


def test_task_updated():
    # Update task
    id = expected_fixture_1['id']
    response = client.put(f"/{id}", json=fixture_1_update)
    assert response.status_code == 200

    # Check update worked
    response = client.get(f"/{id}")
    data = response.json()
    assert expected_fixture_1_after_update == data


############################################################# SORTING

def test_default_sorting_by_task_ascending():
    # Test sorting all items by task ascending
    response = client.get("/")
    expectedOrder = ["Buy Flour", "Clean Loft", "Fix Brakes"]
    actualOrder = []
    for each in response.json():
        actualOrder.append(each["task"])
    assert expectedOrder == actualOrder


def test_sorting_by_task_descending():
    # Test sorting all items by task descending
    response = client.get("/?sortBy=NAME_DESC")
    expectedOrder = ["Fix Brakes", "Clean Loft", "Buy Flour"]
    actualOrder = []
    for each in response.json():
        actualOrder.append(each["task"])
    assert expectedOrder == actualOrder


def test_sorting_by_importance_ascending():
    # Test sorting all items by task ascending
    response = client.get("/?sortBy=IMPORTANCE_ASC")
    expectedOrder = [1, 2, 10]
    actualOrder = []
    for each in response.json():
        actualOrder.append(each["importance"])
    assert expectedOrder == actualOrder


def test_sorting_by_importance_descending():
    # Test sorting all items by task descending
    response = client.get("/?sortBy=IMPORTANCE_DESC")
    expectedOrder = [10, 2, 1]
    actualOrder = []
    for each in response.json():
        actualOrder.append(each["importance"])
    assert expectedOrder == actualOrder
