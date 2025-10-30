"""Database configuration and session management."""
from sqlmodel import SQLModel, create_engine, Session
import os

# Use SQLite for development
DATABASE_URL = "sqlite:///./activities.db"

# Create SQLite engine
engine = create_engine(
    DATABASE_URL, echo=False, connect_args={"check_same_thread": False}
)

def init_db():
    """Create all tables in the database."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Get a new database session."""
    with Session(engine) as session:
        yield session