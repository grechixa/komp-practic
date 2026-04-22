from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TaskCreate(BaseModel):
    task_name: str

tasks = [{"id": 1, "text":"Learn Python"}]

@app.get("/")
def home():
    return {"message": "Server is up"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.post("/tasks")
def create_task(task: TaskCreate):
    new_task = {"id": len(tasks) + 1, "text": task.task_name}
    tasks.append(new_task)
    return new_task
