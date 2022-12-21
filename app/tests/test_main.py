from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from ..main import app, get_session
from ..database import Base


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

@pytest.fixture
def test_db() :
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_add_task(test_db):
    response = client.post("/", json=task_data)
    data = response.json()
    assert response.status_code == 200
    assert data['task'] == task_data['task']
    assert data['importance'] == task_data['importance']
    assert data['completed'] == task_data['completed']

