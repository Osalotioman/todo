# Todo (FastAPI + SQLite)

A small todo app built with **FastAPI** and **SQLite**, with a simple HTML/JS UI.

## Features

- Create / edit / toggle complete / delete todos
- JSON API under `/api/todos`
- SQLite storage (easy to swap later)

## Project layout

- [main.py](main.py) — FastAPI app + routes
- [db.py](db.py) — SQLite helpers
- [views/index.html](views/index.html) — UI
- [static/app.css](static/app.css) — styles
- `data/todos.sqlite3` — created at runtime (ignored by git)

## Run locally

```bash
cd /todo

# if you already have a venv:
. .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open: `http://127.0.0.1:8000`

## API

- `GET /api/todos` → list todos
- `POST /api/todos` → create todo
  - body: `{ "title": "Buy milk" }`
- `PATCH /api/todos/{id}` → update todo
  - body: `{ "completed": true }` or `{ "title": "New title" }`
- `DELETE /api/todos/{id}` → delete todo

## Docker

Build and run:

```bash
docker build -t todo-fastapi .
docker run --rm -p 8000:8000 -e PORT=8000 todo-fastapi
```

Open: `http://127.0.0.1:8000`

## Deploy to Render (Docker)

1. Create a new **Web Service** on Render.
2. Choose **Deploy an existing repository** and select this repo.
3. Select **Docker** as the runtime.

Render sets the `PORT` environment variable automatically; the [Dockerfile](Dockerfile) starts Uvicorn on that port.

### Note about SQLite on Render

SQLite writes to the local filesystem. On Render, the filesystem can be **ephemeral** unless you attach a **Persistent Disk**.

- If you want the data to survive deploys/restarts, attach a disk and mount it (e.g. at `/app/data`).
- If you don’t need persistence, SQLite is fine for demos.
- For production multi-instance setups, you’ll typically switch to Postgres.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
