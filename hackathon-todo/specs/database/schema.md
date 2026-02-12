# Database Schema Specification

## Overview
Database schema for the Hackathon Todo application using SQLModel.

## Entity Relationships
```
User (1) -----> (N) Task
User (1) -----> (N) Conversation
Task (N) -----> (1) Category
Task (N) -----> (N) Tag
Conversation (1) -----> (N) Message
```

## Models

### User Model
```python
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(sa_column=Column(String, unique=True, index=True))
    email: str = Field(sa_column=Column(String, unique=True, index=True))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### Task Model
```python
class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(sa_column=Column(String, index=True))
    description: Optional[str] = None
    status: str = Field(default="pending")  # pending, in_progress, completed
    priority: str = Field(default="medium")  # low, medium, high, urgent
    due_date: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user_id: int = Field(foreign_key="user.id")
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
```

### Category Model
```python
class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(sa_column=Column(String, unique=True, index=True))
    color: str = Field(default="#000000")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user_id: int = Field(foreign_key="user.id")
```

### Conversation Model
```python
class Conversation(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    user_id: int = Field(foreign_key="user.id")
```

### Message Model
```python
class Message(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    content: str
    role: str = Field(default="user")  # user, assistant, system
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    conversation_id: int = Field(foreign_key="conversation.id")
```

## Indexes
- User.username (unique)
- User.email (unique)
- Task.title (index)
- Task.status (index)
- Task.due_date (index)
- Category.name (unique)

## Constraints
- All timestamps are stored in UTC
- Foreign key constraints enforce referential integrity
- Unique constraints prevent duplicate usernames/emails