from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from db import (
	TodoRow,
	create_todo,
	delete_todo,
	get_db,
	init_db,
	list_todos,
	update_todo,
)

app = FastAPI(title="Todo", version="0.1.0")

templates = Jinja2Templates(directory="views")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def _startup() -> None:
	init_db()


@app.get("/health")
def health() -> dict[str, str]:
	return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
	return templates.TemplateResponse("index.html", {"request": request})


class TodoCreateIn(BaseModel):
	title: str = Field(..., min_length=1, max_length=200)


class TodoUpdateIn(BaseModel):
	title: str | None = Field(default=None, min_length=1, max_length=200)
	completed: bool | None = None


class TodoOut(BaseModel):
	id: int
	title: str
	completed: bool
	created_at: str
	updated_at: str


def _to_out(row: TodoRow) -> TodoOut:
	return TodoOut(
		id=row["id"],
		title=row["title"],
		completed=bool(row["completed"]),
		created_at=row["created_at"],
		updated_at=row["updated_at"],
	)


@app.get("/api/todos", response_model=list[TodoOut])
def api_list_todos(db=Depends(get_db)) -> list[TodoOut]:
	rows = list_todos(db)
	return [_to_out(r) for r in rows]


@app.post("/api/todos", response_model=TodoOut, status_code=status.HTTP_201_CREATED)
def api_create_todo(payload: TodoCreateIn, db=Depends(get_db)) -> TodoOut:
	row = create_todo(db, title=payload.title)
	return _to_out(row)


@app.patch("/api/todos/{todo_id}", response_model=TodoOut)
def api_update_todo(todo_id: int, payload: TodoUpdateIn, db=Depends(get_db)) -> TodoOut:
	if payload.title is None and payload.completed is None:
		raise HTTPException(
			status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
			detail="Provide at least one field to update.",
		)
	row = update_todo(db, todo_id=todo_id, title=payload.title, completed=payload.completed)
	if row is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
	return _to_out(row)


@app.delete("/api/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def api_delete_todo(todo_id: int, db=Depends(get_db)) -> None:
	deleted = delete_todo(db, todo_id=todo_id)
	if not deleted:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
