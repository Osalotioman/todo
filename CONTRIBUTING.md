# Contributing

Thanks for contributing!

## Setup

```bash
cd /todo
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload --port 8000
```

Open: `http://127.0.0.1:8000`

## Development notes

- Keep changes focused and incremental.
- Prefer small, reviewable PRs.
- If you change API behavior, update the README section “API”.
- If you change DB schema, consider a migration strategy (even a simple one).

## Pull requests

- Describe *what* changed and *why*.
- Include steps to test locally.
- Avoid committing generated files (e.g. `data/todos.sqlite3`, `.venv/`).
