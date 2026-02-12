"""
Database models for Task, Conversation, and Message entities.

This module defines the SQLModel models with proper relationships and timestamps.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# Forward references need to be handled carefully in Python
class ConversationBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"
    priority: str = "medium"


class MessageBase(BaseModel):
    content: str
    role: str  # user, assistant, system


class Task(TaskBase, SQLModel, table=True):
    """Task model with relationship to Conversation."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Conversation
    conversation_id: Optional[int] = Field(default=None, foreign_key="conversation.id")
    conversation: Optional["Conversation"] = Relationship(back_populates="tasks")


class Conversation(ConversationBase, SQLModel, table=True):
    """Conversation model with relationships to Messages and Tasks."""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation", cascade_delete=True)
    tasks: List["Task"] = Relationship(back_populates="conversation", cascade_delete=True)


class Message(MessageBase, SQLModel, table=True):
    """Message model belonging to a Conversation."""
    id: Optional[int] = Field(default=None, primary_key=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Conversation
    conversation_id: int = Field(foreign_key="conversation.id")
    conversation: "Conversation" = Relationship(back_populates="messages")


# Due to forward references, we need to update the annotations after defining all classes
Conversation.update_forward_refs()
Task.update_forward_refs()