import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from bson import ObjectId
from datetime import datetime, timedelta
import pandas as pd
from main import app, download_and_process_data, collection, CourseModel

client = TestClient(app)

@pytest.fixture
def mock_course():
    return {
        "university": "Test University",
        "city": "Test City",
        "country": "Test Country",
        "courseName": "Test Course",
        "courseDescription": "This is a test course",
        "startDate": datetime.now(),
        "endDate": datetime.now() + timedelta(days=30),
        "price": 100.00,
        "currency": "USD"
    }

@pytest.fixture
def mock_db(monkeypatch):
    async def mock_find(*args, **kwargs):
        return MagicMock()

    async def mock_to_list(*args, **kwargs):
        return [mock_course()]

    async def mock_insert_one(*args, **kwargs):
        return MagicMock(inserted_id=ObjectId())

    async def mock_find_one(*args, **kwargs):
        return mock_course()

    async def mock_find_one_and_update(*args, **kwargs):
        return mock_course()

    async def mock_delete_one(*args, **kwargs):
        return MagicMock(deleted_count=1)

    monkeypatch.setattr(collection, "find", mock_find)
    monkeypatch.setattr(collection, "insert_one", mock_insert_one)
    monkeypatch.setattr(collection, "find_one", mock_find_one)
    monkeypatch.setattr(collection, "find_one_and_update", mock_find_one_and_update)
    monkeypatch.setattr(collection, "delete_one", mock_delete_one)
    monkeypatch.setattr(MagicMock, "to_list", mock_to_list)

@pytest.mark.asyncio
async def test_download_and_process_data(monkeypatch):
    mock_response = MagicMock()
    mock_response.text = "University,City,Country,CourseName,CourseDescription,StartDate,EndDate,Price,Currency\nMock Uni,Mock City,Mock Country,Mock Course,Description,2023-01-01,2023-12-31,1000,USD"
    
    async def mock_delete_many(*args, **kwargs):
        return MagicMock()

    async def mock_insert_many(*args, **kwargs):
        return MagicMock()

    async def mock_create_indexes(*args, **kwargs):
        return MagicMock()

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_response)
    monkeypatch.setattr(collection, "delete_many", mock_delete_many)
    monkeypatch.setattr(collection, "insert_many", mock_insert_many)
    monkeypatch.setattr(collection, "create_indexes", mock_create_indexes)

    await download_and_process_data()

def test_create_course(mock_db):
    course_data = CourseModel(**mock_course())
    response = client.post("/courses", json=course_data.dict())
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_courses(mock_db):
    response = client.get("/courses")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_update_course(mock_db):
    course_id = str(ObjectId())
    course_data = CourseModel(**mock_course())
    response = client.put(f"/courses/{course_id}", json=course_data.dict())
    assert response.status_code == 200
    assert response.json()["id"] == course_id

def test_delete_course(mock_db):
    course_id = str(ObjectId())
    response = client.delete(f"/courses/{course_id}")
    assert response.status_code == 200
    assert response.json() == {"message": "Course deleted successfully"}

def test_get_courses_with_search(mock_db):
    response = client.get("/courses?search=Test")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_courses_pagination(mock_db):
    response = client.get("/courses?page=1&per_page=5")
    assert response.status_code == 200
    assert len(response.json()) <= 5

@pytest.mark.asyncio
async def test_periodic_refresh(monkeypatch):
    mock_sleep = MagicMock()
    mock_download = MagicMock()
    
    monkeypatch.setattr(asyncio, "sleep", mock_sleep)
    monkeypatch.setattr("main.download_and_process_data", mock_download)
    
    # Run the periodic_refresh function for a short time
    task = asyncio.create_task(app.periodic_refresh())
    await asyncio.sleep(0.1)
    task.cancel()
    
    mock_sleep.assert_called_with(600)
    mock_download.assert_called()