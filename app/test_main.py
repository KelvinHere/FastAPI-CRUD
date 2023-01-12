from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

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
fixture_4 = '''INSERT INTO items (task, importance, completed, 'created') VALUES ('Buy Eggs', 2, false, '2022-12-21 16:33:41')'''

# Expected responses
expected_fixture_1 = {'completed': True, 'importance': 2, 'id': 1, 'task': 'Clean Loft', 'created': '2022-12-21T12:30:01'}
expected_fixture_2 = {'completed': False, 'importance': 10, 'id': 2, 'task': 'Fix Brakes', 'created': '2022-12-21T12:35:01'}
expected_fixture_3 = {'completed': False, 'importance': 1, 'id': 3, 'task': 'Buy Flour', 'created': '2022-12-21T16:33:31'}
expected_fixture_4 = {'completed': False, 'importance': 2, 'id': 4, 'task': 'Buy Eggs', 'created': '2022-12-21T16:33:41'}
expected_added_task = {'completed': False, 'importance': 4, 'id': 5, 'task': 'Go Fishing', 'created': '2022-12-22T10:42:10'}
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
    engine.execute(fixture_4)
    yield
    Base.metadata.drop_all(bind=engine)


def test_db_fixtures_loaded():
    response = client.get("/")
    data = response.json()
    assert expected_fixture_1 in data
    assert expected_fixture_2 in data
    assert expected_fixture_3 in data
    assert expected_fixture_4 in data


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
    expectedOrder = ["Buy Eggs", "Buy Flour", "Clean Loft", "Fix Brakes"]
    actualOrder = []
    for each in response.json():
        actualOrder.append(each["task"])
    assert expectedOrder == actualOrder


def test_sorting_by_task_descending():
    # Test sorting all items by task descending
    response = client.get("/?sortBy=NAME_DESC")
    expectedOrder = ["Fix Brakes", "Clean Loft", "Buy Flour", "Buy Eggs"]
    actualOrder = []
    for each in response.json():
        actualOrder.append(each["task"])
    assert expectedOrder == actualOrder


def test_sorting_by_importance_ascending():
    # Test sorting all items by task ascending
    response = client.get("/?sortBy=IMPORTANCE_ASC")
    expectedOrder = [1, 2, 2, 10]
    actualOrder = []
    for each in response.json():
        actualOrder.append(each["importance"])
    assert expectedOrder == actualOrder


def test_sorting_by_importance_descending():
    # Test sorting all items by task descending
    response = client.get("/?sortBy=IMPORTANCE_DESC")
    expectedOrder = [10, 2, 2, 1]
    actualOrder = []
    for each in response.json():
        actualOrder.append(each["importance"])
    assert expectedOrder == actualOrder


############################################################# QUERY
def test_query():
    # Test query only returns relevant results
    response = client.get("/?q=Fix")
    expectedResponse = expected_fixture_2
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert expectedResponse == response.json()[0]


def test_query_with_two_results():
    # Test query only returns relevant results
    response = client.get("/?q=Buy")
    data = response.json()
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert expected_fixture_3 in data
    assert expected_fixture_4 in data


def test_query_no_results():
    # Test query returns correct status code and no results
    response = client.get("/?q=NothingIsGoingToBeReturnedFromThis")
    print(response.status_code)
    assert response.status_code == 200
    assert len(response.json()) == 0



############################################################# RESULTS QUANTITY
def test_only_3_results_returned():
    # Result limited to only allow 3 results returned
    response = client.get("/?resultQty=3")
    assert response.status_code == 200
    assert len(response.json()) == 3

def test_only_1_results_returned():
    # Result limited to only allow 1 results returned
    response = client.get("/?resultQty=1")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_invalid_resultQty_input():
    # Correct error message delivered if invalid quantity input
    response = client.get("/?resultQty=NaN")
    assert response.status_code == 422


############################################################# QUERY & SORT
def test_query_and_sort_tasks_ascending():
    # Test filtered results are sorted by task name ascending
    response = client.get("/?q=Buy&sortBy=NAME_ASC")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert expected_fixture_3 == response.json()[1]
    assert expected_fixture_4 == response.json()[0]


def test_query_and_sort_tasks_ascending():
    # Test filtered results are sorted by task name descending
    response = client.get("/?q=Buy&sortBy=NAME_DESC")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert expected_fixture_3 == response.json()[0]
    assert expected_fixture_4 == response.json()[1]


def test_query_and_sort_importance_ascending():
    # Test filtered results are sorted by importance ascending
    response = client.get("/?q=Buy&sortBy=IMPORTANCE_ASC")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert expected_fixture_3 == response.json()[0]
    assert expected_fixture_4 == response.json()[1]


def test_query_and_sort_importance_descending():
    # Test filtered results are sorted by importance descending
    response = client.get("/?q=Buy&sortBy=IMPORTANCE_DESC")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert expected_fixture_3 == response.json()[1]
    assert expected_fixture_4 == response.json()[0]


############################################################# SORT & QUANTITY
def test_quantity_and_sort_importance_descending():
    # Test filtered results are sorted by importance descending
    response = client.get("/?sortBy=IMPORTANCE_DESC&resultQty=3")
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert expected_fixture_2 == response.json()[0]
    assert expected_fixture_1 == response.json()[1]
    assert expected_fixture_4 == response.json()[2]

