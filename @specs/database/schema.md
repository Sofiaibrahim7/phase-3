# Database Schema Specification

This document defines the SQLModel database schema for the application.

## Models

### Task Model
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    status: str = Field(default="pending")  # pending, in_progress, completed
    priority: str = Field(default="medium")  # low, medium, high
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation_id: Optional[int] = Field(default=None, foreign_key="conversation.id")
    conversation: Optional["Conversation"] = Relationship(back_populates="tasks")
```

### Conversation Model
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Conversation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    messages: List["Message"] = Relationship(back_populates="conversation")
    tasks: List["Task"] = Relationship(back_populates="conversation")
```

### Message Model
```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional, List

class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    role: str = Field(index=True)  # user, assistant, system
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    conversation_id: int = Field(foreign_key="conversation.id")
    conversation: "Conversation" = Relationship(back_populates="messages")
```

## Relationship Diagram
```
Conversation (1) <---> (N) Message
Conversation (1) <---> (N) Task
```

## Indexes
- Task.title
- Conversation.title
- Message.role
- Message.timestamp

## Notes
- All models include created_at and updated_at timestamps
- Foreign key relationships are properly defined
- Optional fields are marked as Optional[type]
- Status and priority fields have default values for Task model
