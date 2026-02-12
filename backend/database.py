from sqlmodel import SQLModel, Field, create_engine, Session
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, String
import os
from sqlmodel import Relationship, select


class Task(SQLModel, table=True):
    __tablename__ = "task"

    id: int = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String, index=True))
    description: Optional[str] = None
    status: str = Field(default="pending")  # pending, in_progress, completed
    priority: str = Field(default="medium")  # low, medium, high, urgent
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships - Removed foreign key references since User and Category models are removed
    user_id: int  # No foreign key constraint since User model is removed
    category_id: Optional[int] = None  # No foreign key constraint since Category model is removed


class Conversation(SQLModel, table=True):
    __tablename__ = "conversation"

    id: int = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships - Removed foreign key reference since User model is removed
    user_id: int  # No foreign key constraint since User model is removed


class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: int = Field(default=None, primary_key=True)
    content: str
    role: str = Field(default="user")  # user, assistant, system
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation_id: int = Field(foreign_key="conversation.id")


# Database setup
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")
engine = create_engine(DATABASE_URL)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session