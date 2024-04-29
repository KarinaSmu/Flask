from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class Task(BaseModel):
    title: str
    description: str
    status: bool

tasks_db = []

@app.get("/tasks", response_model=List[Task])
async def read_tasks():
    return tasks_db

@app.get("/tasks/{task_id}", response_model=Task)
async def read_task(task_id: int):
    for task in tasks_db:
        if task.get("id") == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", response_model=Task)
async def create_task(task: Task):
    task_data = task.dict()
    task_data["id"] = len(tasks_db) + 1
    tasks_db.append(task_data)
    return task_data

@app.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task: Task):
    for existing_task in tasks_db:
        if existing_task.get("id") == task_id:
            existing_task.update(task.dict())
            return existing_task
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    for index, existing_task in enumerate(tasks_db):
        if existing_task.get("id") == task_id:
            del tasks_db[index]
            return {"message": "Task deleted successfully"}
    raise HTTPException(status_code=404, detail="Task not found")
