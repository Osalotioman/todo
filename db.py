from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, TypedDict


class TodoRow(TypedDict):
    id: int
    title: str
    completed: int
    created_at: str
    updated_at: str


_DATA_DIR = Path(__file__).resolve().parent / "data"
_DB_PATH = _DATA_DIR / "todos.sqlite3"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def init_db() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(_DB_PATH)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS todos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def get_db() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def list_todos(conn: sqlite3.Connection) -> list[TodoRow]:
    cur = conn.execute(
        "SELECT id, title, completed, created_at, updated_at FROM todos ORDER BY id DESC"
    )
    rows = cur.fetchall()
    return [dict(r) for r in rows]  # type: ignore[return-value]


def get_todo(conn: sqlite3.Connection, todo_id: int) -> TodoRow | None:
    cur = conn.execute(
        "SELECT id, title, completed, created_at, updated_at FROM todos WHERE id = ?",
        (todo_id,),
    )
    row = cur.fetchone()
    return dict(row) if row else None  # type: ignore[return-value]


def create_todo(conn: sqlite3.Connection, title: str) -> TodoRow:
    now = _utc_now_iso()
    cur = conn.execute(
        "INSERT INTO todos (title, completed, created_at, updated_at) VALUES (?, 0, ?, ?)",
        (title.strip(), now, now),
    )
    if cur.lastrowid is None:
        raise RuntimeError("Failed to create todo (no lastrowid)")
    todo_id = int(cur.lastrowid)
    row = get_todo(conn, todo_id)
    assert row is not None
    return row


def update_todo(
    conn: sqlite3.Connection,
    todo_id: int,
    *,
    title: str | None,
    completed: bool | None,
) -> TodoRow | None:
    existing = get_todo(conn, todo_id)
    if existing is None:
        return None

    new_title = existing["title"] if title is None else title.strip()
    new_completed = existing["completed"] if completed is None else (1 if completed else 0)

    conn.execute(
        "UPDATE todos SET title = ?, completed = ?, updated_at = ? WHERE id = ?",
        (new_title, new_completed, _utc_now_iso(), todo_id),
    )
    return get_todo(conn, todo_id)


def delete_todo(conn: sqlite3.Connection, todo_id: int) -> bool:
    cur = conn.execute("DELETE FROM todos WHERE id = ?", (todo_id,))
    return cur.rowcount > 0
