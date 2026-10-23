# Git Practice Task API

A small FastAPI + SQLite backend for practicing Git. Requires Python 3.10+.
SQLite is included with Python; no database server is needed.

## Run locally

From this folder, run:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m uvicorn main:app --reload
```

On Windows, activate with `.venv\Scripts\activate` instead.

Open http://127.0.0.1:8000/docs to try every endpoint in your browser.
The app creates `tasks.db` on startup. Tasks survive server restarts.
Stop the server with Ctrl+C.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/` | Welcome message |
| POST | `/tasks` | Create a task |
| GET | `/tasks` | List tasks |
| GET | `/tasks/{task_id}` | Get one task |
| PUT | `/tasks/{task_id}` | Replace title and completed state |
| DELETE | `/tasks/{task_id}` | Delete a task |

Create or replace a task with JSON:

```json
{"title": "Practice Git branches", "completed": false}
```

Titles must contain 1–200 characters after trimming whitespace. Missing tasks
return 404; invalid input returns 422. PUT defaults `completed` to false if omitted.

## How the code fits together

- `main.py`: request models, API routes, and SQLite queries.
- `test_main.py`: API tests using a separate temporary database.
- `requirements.txt`: runtime dependencies.
- `requirements-dev.txt`: runtime dependencies plus testing tools.
- `.gitignore`: keeps local databases, virtual environments, and caches out of Git.

Run tests with your virtual environment activated:

```bash
python -m pytest -q
```

## Practice Git

The repository is intentionally not initialized so you can do the first steps.

1. Create a repository and your first commit:

   ```bash
   git init -b main
   git status
   git add .
   git commit -m "Add task API with SQLite"
   ```

   If Git asks for your identity, configure `user.name` and `user.email` with
   `git config` and then retry the commit.

2. Create a feature branch:

   ```bash
   git switch -c feature/welcome-message
   ```

   Change the welcome message in `main.py`, then inspect and commit it:

   ```bash
   git diff
   python -m pytest -q
   git add main.py
   git commit -m "Update welcome message"
   ```

3. Merge your feature into main:

   ```bash
   git switch main
   git merge feature/welcome-message
   git log --oneline --graph --all
   ```

4. Practice more changes, using a separate branch and commit for each:
   - Add a `/health` endpoint returning `{"status": "ok"}`.
   - Add a query parameter to filter tasks by completion.
   - Add a test for the new behavior.
   - Change the same welcome message on two branches, then merge both to
     practice resolving a conflict.

Use `git status` and `git diff` often. To unstage a file while keeping edits,
use `git restore --staged <file>` after your first commit.

FastAPI reference: https://fastapi.tiangolo.com/tutorial/first-steps/

This is a local learning app without authentication.
