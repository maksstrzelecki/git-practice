import sqlite3

import pytest
from fastapi.testclient import TestClient

import main


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DATABASE_PATH", tmp_path / "test.db")
    with TestClient(main.app) as client:
        yield client


def test_task_lifecycle_and_persistence(client):
    assert client.get("/tasks").json() == []
    created = client.post("/tasks", json={"title": "Learn Git"})
    assert created.status_code == 201
    task = created.json()
    assert task == {"id": 1, "title": "Learn Git", "completed": False}
    assert client.get("/tasks/1").json() == task
    assert client.get("/tasks").json() == [task]

    updated = client.put("/tasks/1", json={"title": "Make a commit", "completed": True})
    assert updated.status_code == 200
    assert updated.json()["completed"] is True
    with sqlite3.connect(main.DATABASE_PATH) as connection:
        assert connection.execute("SELECT title, completed FROM tasks").fetchone() == (
            "Make a commit", 1
        )

    assert client.delete("/tasks/1").status_code == 204
    assert client.get("/tasks/1").status_code == 404
    assert client.get("/tasks").json() == []


def test_validation_and_missing_tasks(client):
    for title in ["", "   ", "x" * 201]:
        assert client.post("/tasks", json={"title": title}).status_code == 422
    assert client.get("/tasks/999").status_code == 404
    assert client.put("/tasks/999", json={"title": "Missing"}).status_code == 404
    assert client.delete("/tasks/999").status_code == 404
