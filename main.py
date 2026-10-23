"""A small task API for learning Python, SQLite, and Git."""

import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

DATABASE_PATH = Path(__file__).parent / "tasks.db"


@contextmanager
def database():
    """Open one connection per operation and always close it."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        with connection:
            yield connection
    finally:
        connection.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    with database() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )"""
        )
    yield


app = FastAPI(title="Git Practice Task API", lifespan=lifespan)


class TaskInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=200)
    completed: bool = False


class Task(TaskInput):
    id: int


@app.get("/")
def root():
    return {"message": "Set welcome to AB", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "running"}

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskInput):
    with database() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, completed) VALUES (?, ?)",
            (task.title, task.completed),
        )
        return {"id": cursor.lastrowid, **task.model_dump()}


@app.get("/tasks", response_model=list[Task])
def list_tasks():
    with database() as connection:
        return [dict(row) for row in connection.execute("SELECT * FROM tasks ORDER BY id")]


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    with database() as connection:
        row = connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return dict(row)


@app.put("/tasks/{task_id}", response_model=Task)
def replace_task(task_id: int, task: TaskInput):
    """Replace a task's title and completed state."""
    with database() as connection:
        cursor = connection.execute(
            "UPDATE tasks SET title = ?, completed = ? WHERE id = ?",
            (task.title, task.completed, task_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        return {"id": task_id, **task.model_dump()}


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with database() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
