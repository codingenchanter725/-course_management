## Prerequisites

Python 3.11+
MongoDB

## Create a virtual environment:

`python -m venv venv`
`source venv/bin/activate` # On Windows use `venv\Scripts\activate`

## Install dependencies:

`pip install -r requirements.txt`

## Running the Application

Start the FastAPI server:
`uvicorn main:app --reload`

The API will be available at http://localhost:8000

## API Endpoints

GET /courses: Retrieve courses (with pagination and search)
POST /courses: Create a new course
PUT /courses/{course_id}: Update an existing course
DELETE /courses/{course_id}: Delete a course

## Testing

## Install Test Packages

`pip install pytest pytest-asyncio httpx`

## Run tests using pytest:

`pytest test_main.py`
