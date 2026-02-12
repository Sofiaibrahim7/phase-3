"""
Test script to verify the SQLModel models for Task, Conversation, and Message.
"""

from datetime import datetime
from models.database_models import Task, Conversation, Message, TaskStatus, PriorityLevel, RoleType


def test_models():
    """Test the creation and relationships of the models."""
    
    # Create a conversation
    conversation = Conversation(
        title="Project Discussion",
        description="Discussion about the new project implementation"
    )
    
    print("Created conversation:")
    print(f"  ID: {conversation.id}")
    print(f"  Title: {conversation.title}")
    print(f"  Created: {conversation.created_at}")
    print()
    
    # Create a task associated with the conversation
    task = Task(
        title="Implement user authentication",
        description="Create login and signup functionality",
        status=TaskStatus.IN_PROGRESS,
        priority=PriorityLevel.HIGH
    )
    
    print("Created task:")
    print(f"  ID: {task.id}")
    print(f"  Title: {task.title}")
    print(f"  Status: {task.status}")
    print(f"  Priority: {task.priority}")
    print()
    
    # Create a message associated with the conversation
    message = Message(
        content="We need to implement user authentication as soon as possible.",
        role=RoleType.USER
    )
    
    print("Created message:")
    print(f"  ID: {message.id}")
    print(f"  Content: {message.content}")
    print(f"  Role: {message.role}")
    print(f"  Timestamp: {message.timestamp}")
    print()
    
    # Demonstrate relationships (these would be set when actually using with a database session)
    # For demonstration purposes only
    print("Model definitions completed successfully!")
    print("Relationships:")
    print("  - Conversation can have multiple Messages and Tasks")
    print("  - Task belongs to one Conversation (optional)")
    print("  - Message belongs to one Conversation")


if __name__ == "__main__":
    test_models()