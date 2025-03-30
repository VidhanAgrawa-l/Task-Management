from fastapi import FastAPI, Request, status, Depends
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse
import os
from dotenv import load_dotenv
from .database import engine, get_db
from routers import auth, todos, admin, users

# Load environment variables
load_dotenv()

app = FastAPI()

# Ensure static files path is correct
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def test():
    """Redirect root to the main todo page"""
    return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/healthy")
def health_check(db=Depends(get_db)):
    """Health check endpoint to verify API and DB connectivity"""
    try:
        db.execute("SELECT 1")  # Simple DB check
        return {"status": "Healthy", "db": "Connected"}
    except Exception:
        return {"status": "Unhealthy", "db": "Disconnected"}

# Include routers
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)

