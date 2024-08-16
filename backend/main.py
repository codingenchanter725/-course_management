import pandas as pd
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING
from datetime import datetime, timedelta
import asyncio
import requests
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

app = FastAPI()

# MongoDB connection
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.courses_db
collection = db.courses

class CourseModel(BaseModel):
    university: str
    city: str
    country: str
    courseName: str
    courseDescription: str
    startDate: datetime
    endDate: datetime
    price: float
    currency: str

class CourseInDB(CourseModel):
    id: str

async def download_and_process_data():
    url = "https://api.mockaroo.com/api/501b2790?count=100&key=8683a1c0"
    response = requests.get(url)
    df = pd.read_csv(pd.compat.StringIO(response.text))
    
    df['StartDate'] = pd.to_datetime(df['StartDate'])
    df['EndDate'] = pd.to_datetime(df['EndDate'])
    
    courses = df.to_dict('records')
    
    await collection.delete_many({})
    await collection.insert_many(courses)
    
    index_model = IndexModel([("createdAt", ASCENDING)], expireAfterSeconds=600)
    await collection.create_indexes([index_model])
    
    print("Data updated and TTL index created")

@app.on_event("startup")
async def startup_event():
    await download_and_process_data()
    asyncio.create_task(periodic_refresh())

async def periodic_refresh():
    while True:
        await asyncio.sleep(600)  # Wait for 10 minutes
        await download_and_process_data()

@app.get("/courses", response_model=List[CourseInDB])
async def get_courses(search: Optional[str] = None, page: int = 1, per_page: int = 10):
    skip = (page - 1) * per_page
    query = {}
    if search:
        query = {
            "$or": [
                {"university": {"$regex": search, "$options": "i"}},
                {"city": {"$regex": search, "$options": "i"}},
                {"country": {"$regex": search, "$options": "i"}},
                {"courseName": {"$regex": search, "$options": "i"}},
                {"courseDescription": {"$regex": search, "$options": "i"}},
            ]
        }
    
    cursor = collection.find(query).skip(skip).limit(per_page)
    courses = await cursor.to_list(length=per_page)
    return [CourseInDB(**{**course, "id": str(course["_id"])}) for course in courses]

@app.put("/courses/{course_id}", response_model=CourseInDB)
async def update_course(course_id: str, course: CourseModel):
    updated_course = await collection.find_one_and_update(
        {"_id": ObjectId(course_id)},
        {"$set": course.dict()},
        return_document=True
    )
    if updated_course:
        return CourseInDB(**{**updated_course, "id": str(updated_course["_id"])})
    raise HTTPException(status_code=404, detail="Course not found")

@app.delete("/courses/{course_id}")
async def delete_course(course_id: str):
    result = await collection.delete_one({"_id": ObjectId(course_id)})
    if result.deleted_count:
        return {"message": "Course deleted successfully"}
    raise HTTPException(status_code=404, detail="Course not found")

@app.post("/courses", response_model=CourseInDB)
async def create_course(course: CourseModel):
    new_course = await collection.insert_one(course.dict())
    created_course = await collection.find_one({"_id": new_course.inserted_id})
    return CourseInDB(**{**created_course, "id": str(created_course["_id"])})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)