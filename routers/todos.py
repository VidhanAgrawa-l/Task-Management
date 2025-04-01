from typing import Annotated, Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from ..models import Todos, TaskCategory
from ..database import SessionLocal
from .auth import get_current_user

templates = Jinja2Templates(directory="TodoApp/templates")

router = APIRouter(
    prefix='/todos',
    tags=['todos']
)

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# Pydantic Model for Requests
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool
    category: TaskCategory  # New: Eisenhower Matrix Category

# Redirect Helper
def redirect_to_login():
    response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

### Pages ###
@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
        return templates.TemplateResponse("todo.html", {"request": request, "todos": todos, "user": user})

    except:
        return redirect_to_login()

@router.get('/add-todo-page')
async def render_add_todo_page(request: Request):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html", {"request": request, "user": user})

    except:
        return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
    try:
        user = await get_current_user(request.cookies.get('access_token'))
        if user is None:
            return redirect_to_login()

        todo = db.query(Todos).filter(Todos.id == todo_id).first()
        return templates.TemplateResponse("edit-todo.html", {"request": request, "todo": todo, "user": user})

    except:
        return redirect_to_login()

### API Endpoints ###

# Get all tasks with optional filtering
@router.get("/", status_code=status.HTTP_200_OK, response_model=List[TodoRequest])
async def read_all(
    user: user_dependency,
    db: db_dependency,
    category: Optional[TaskCategory] = Query(None), 
    completed: Optional[bool] = Query(None),
    priority: Optional[int] = Query(None)
):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    query = db.query(Todos).filter(Todos.owner_id == user.get('id'))

    if category:
        query = query.filter(Todos.category == category)
    if completed is not None:
        query = query.filter(Todos.complete == completed)
    if priority:
        query = query.filter(Todos.priority == priority)

    return query.all()

# Get a single task
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get('id')).first()
    if todo_model:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found.')

# Create a new task
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)  # Return created item
    return todo_model

# Update a task
@router.put("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete
    todo_model.category = todo_request.category  # Update category

    db.commit()
    db.refresh(todo_model)
    return todo_model

# Delete a task
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication Failed')

    todo_model = db.query(Todos).filter(Todos.id == todo_id, Todos.owner_id == user.get('id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')

    db.delete(todo_model)
    db.commit()
