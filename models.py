from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base
import enum

# Enum for Eisenhower Matrix categories
class TaskCategory(enum.Enum):
    DO = "Do"
    SCHEDULE = "Schedule"
    DELEGATE = "Delegate"
    ELIMINATE = "Eliminate"

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(50), default="user")
    phone_number = Column(String(15), unique=True, nullable=True)

    # Relationship: One user can have many tasks
    todos = relationship("Todos", back_populates="owner")

class Todos(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500))
    priority = Column(Integer, nullable=False)  # 1 (low) → 5 (high)
    complete = Column(Boolean, default=False)
    category = Column(Enum(TaskCategory), nullable=False)  # Eisenhower Matrix category
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("Users", back_populates="todos")
