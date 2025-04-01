import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read DB URL from .env file (defaulting to PostgreSQL for production)
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todosapp.db")

# Create engine (PostgreSQL or SQLite fallback)
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)  # PostgreSQL engine

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define Base class
Base = declarative_base()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
