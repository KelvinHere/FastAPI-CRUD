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

# Change app dependancy to new test DB
app.dependency_overrides[get_session] = override_get_session


client = TestClient(app)


task_data = {
    "task": "Test Task",
    "importance": 4,
    "completed": False
}

fix1 = {
    "task": "fixturetask1",
    "importance": 2,
    "completed": True
}

fixture_1 = '''INSERT INTO items (task, importance, completed, 'created') VALUES ('FixtureTask1', 2, true, '2022-12-21 12:30:01')'''
fixture_1_json = {'completed': True, 'importance': 2, 'id': 1, 'task': 'FixtureTask1', 'created': '2022-12-21T12:30:01'}
fixture_1_json_update = {'completed': False, 'importance': 9, 'task': 'FixtureTask1Updated'}
expected_fixture_1_json_after_update = {'completed': False, 'importance': 9, 'id': 1, 'task': 'FixtureTask1Updated', 'created': '2022-12-21T12:30:01'}
fixture_2 = '''INSERT INTO items (task, importance, completed, 'created') VALUES ('FixtureTask2', 10, false, '2022-12-21 12:35:01')'''
fixture_2_json = {'completed': False, 'importance': 10, 'id': 2, 'task': 'FixtureTask2', 'created': '2022-12-21T12:35:01'}


@pytest.fixture(autouse=True)
def setup_db() :
    Base.metadata.create_all(bind=engine)
    engine.execute(fixture_1)
    engine.execute(fixture_2)
    yield
    Base.metadata.drop_all(bind=engine)


def test_db_fixtures_loaded():
    response = client.get("/")
    data = response.json()
    assert fixture_1_json in data
    assert fixture_2_json in data


def test_add_task():
    #Tests adding a task to the database
    response = client.post("/", json=task_data)
    data = response.json()
    assert response.status_code == 200
    assert data['task'] == task_data['task']
    assert data['importance'] == task_data['importance']
    assert data['completed'] == task_data['completed']


def test_delete_task():
    #Add task to be deleted & confirm it exists
    response = client.post("/", json=task_data)
    data = response.json()
    assert response.status_code == 200
    assert data['task'] == task_data['task']
    assert data['importance'] == task_data['importance']
    assert data['completed'] == task_data['completed']
    item_id = data['id']

    #Test task is deleted
    response = client.delete(f"/{item_id}")
    assert response.status_code == 200
    assert task_data['task'] not in response.json()


def test_task_updated():
    # Update task
    id = fixture_1_json['id']
    response = client.put(f"/{id}", json=fixture_1_json_update)
    assert response.status_code == 200

    # Check update worked
    response = client.get(f"/{id}")
    data = response.json()
    assert expected_fixture_1_json_after_update == data
    