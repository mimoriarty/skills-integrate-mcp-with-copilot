"""Database models for the application."""
from sqlmodel import SQLModel, Field
from typing import List, Optional
from datetime import datetime

class Activity(SQLModel, table=True):
    """Activity model representing an extracurricular activity."""
    name: str = Field(primary_key=True)
    description: str
    schedule: str
    max_participants: int

class Participant(SQLModel, table=True):
    """Participant model representing a student signed up for an activity."""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    activity_name: str = Field(foreign_key="activity.name")
    registered_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """SQLModel configuration."""
        table = True