"""
SQLModel models for Task, Conversation, and Message with relationships and timestamps.

This module defines the database models with proper relationships, validation,
and helper methods for a task management and conversation system.
"""

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
import enum


if TYPE_CHECKING:
    from typing import List  # noqa: F401


class TaskStatus(str, enum.Enum):
    """Enumeration for task statuses."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class PriorityLevel(str, enum.Enum):
    """Enumeration for priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class RoleType(str, enum.Enum):
    """Enumeration for message roles."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class Task(SQLModel, table=True):
    """
    Task model representing a unit of work.
    
    Attributes:
        id: Unique identifier for the task
        title: Title of the task
        description: Detailed description of the task
        status: Current status of the task (pending, in_progress, completed, cancelled)
        priority: Priority level of the task (low, medium, high, urgent)
        created_at: Timestamp when the task was created
        updated_at: Timestamp when the task was last updated
        conversation_id: Foreign key linking to the associated conversation
    """
    __tablename__ = "task"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    priority: PriorityLevel = Field(default=PriorityLevel.MEDIUM)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Conversation
    conversation_id: Optional[int] = Field(default=None, foreign_key="conversation.id")
    conversation: Optional["Conversation"] = Relationship(back_populates="tasks")


class Conversation(SQLModel, table=True):
    """
    Conversation model representing a discussion thread.
    
    Attributes:
        id: Unique identifier for the conversation
        title: Title of the conversation
        description: Description of the conversation
        created_at: Timestamp when the conversation was created
        updated_at: Timestamp when the conversation was last updated
    """
    __tablename__ = "conversation"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships - using string references to handle circular dependencies
    messages: List["Message"] = Relationship(
        back_populates="conversation",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    tasks: List["Task"] = Relationship(
        back_populates="conversation", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class Message(SQLModel, table=True):
    """
    Message model representing a single message in a conversation.
    
    Attributes:
        id: Unique identifier for the message
        content: Content of the message
        role: Role of the sender (user, assistant, system)
        timestamp: Timestamp when the message was sent
        created_at: Timestamp when the message record was created
        updated_at: Timestamp when the message record was last updated
        conversation_id: Foreign key linking to the associated conversation
    """
    __tablename__ = "message"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(min_length=1, max_length=5000)
    role: RoleType = Field(index=True)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationship to Conversation
    conversation_id: int = Field(foreign_key="conversation.id")
    conversation: "Conversation" = Relationship(back_populates="messages")


# Update forward references to handle circular dependencies
Conversation.update_forward_refs()
Task.update_forward_refs()
Message.update_forward_refs()


# Pydantic configuration for serialization
def get_serializable_dict(model_instance: SQLModel) -> dict:
    """
    Helper function to get a serializable dictionary representation of a model instance.
    
    Args:
        model_instance: An instance of a SQLModel
        
    Returns:
        Dictionary representation of the model instance
    """
    return model_instance.dict(exclude_unset=True)