import sqlite3

from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse


app = FastAPI()
def get_db_connection():
    connection = sqlite3.connect("tasks.db")
    connection.row_factory = sqlite3.Row
    return connection

def create_table():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)

    connection.commit()
    connection.close()

def seed_tasks():
    connection = get_db_connection()

    count = connection.execute("" \
        "SELECT COUNT (*) FROM tasks"
    ).fetchone()[0]

    if count == 0:
        connection.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy Milk", False),
                ("Complete Internship Assignment", False),
                ("Go to the gym", True)
            ]
        )

        connection.commit()

    connection.close()

create_table()
seed_tasks()

tasks = [
    {"id": 1, "title": "Buy Milk", "done": False},
    {"id": 2, "title": "Complete Internship Assignment", "done": False},
    {"id": 3, "title": "Go to the gym", "done": True}
]

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

@app.get("/", description="Shows basic information about the Task API")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", description="Checks that the API server is running")
def health():
    return {
        "status": "ok"
    }

@app.get("/tasks", description="Returns all tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}", description="Returns a single task by its ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

@app.post("/tasks", status_code=201, description="Create a new task")
def create_task(task: TaskCreate):
    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannont be empty"}
        )

    new_task = {
        "id": max(t["id"] for t in tasks) + 1,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", description="Updates an existing task")
def update_task(task_id: int, task: TaskUpdate):
    for existing_task in tasks:
        if existing_task["id"] == task_id:

            if task.title is not None:
                if not task.title.strip():
                    return JSONResponse(
                        status_code=400,
                        content={"error": "Title cannot be empty"}
                    )
                existing_task["title"] = task.title

            if task.done is not None:
                existing_task["done"] = task.done

            return existing_task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )

@app.delete("/tasks/{task_id}", status_code=204, description="Deletes a task")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )