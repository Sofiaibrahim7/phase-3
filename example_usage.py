"""
Example demonstrating how to use the SQLModel models with a database session.
"""

from datetime import datetime
from sqlmodel import SQLModel, create_engine, Session, select
from models.database_models import Task, Conversation, Message, TaskStatus, PriorityLevel, RoleType


def create_db_and_tables():
    """Create database tables."""
    engine = create_engine("sqlite:///task_conversation_message.db")
    SQLModel.metadata.create_all(engine)
    return engine


def create_sample_data(engine):
    """Create sample data using the models."""
    with Session(engine) as session:
        # Create a conversation
        conversation = Conversation(
            title="Project Planning Meeting",
            description="Initial meeting to discuss project requirements"
        )
        
        # Add the conversation to the session
        session.add(conversation)
        session.commit()
        # Refresh to get the ID
        session.refresh(conversation)
        
        print(f"Created conversation: {conversation.title} (ID: {conversation.id})")
        
        # Create a task associated with the conversation
        task = Task(
            title="Design database schema",
            description="Create ERD and define all necessary tables",
            status=TaskStatus.PENDING,
            priority=PriorityLevel.HIGH,
            conversation_id=conversation.id
        )
        
        session.add(task)
        session.commit()
        session.refresh(task)
        
        print(f"Created task: {task.title} (ID: {task.id})")
        
        # Create messages for the conversation
        message1 = Message(
            content="Hello team, let's start discussing the project requirements.",
            role=RoleType.ASSISTANT,
            conversation_id=conversation.id
        )
        
        message2 = Message(
            content="Sure, I think we should start with the database design.",
            role=RoleType.USER,
            conversation_id=conversation.id
        )
        
        session.add(message1)
        session.add(message2)
        session.commit()
        
        session.refresh(message1)
        session.refresh(message2)
        
        print(f"Created messages: {message1.id} and {message2.id}")
        
        # Query and display the data
        print("\n--- Retrieved Data ---")
        
        # Get the conversation with its tasks and messages
        statement = select(Conversation).where(Conversation.id == conversation.id)
        result = session.exec(statement).one()
        print(f"Conversation: {result.title}")
        print(f"Description: {result.description}")
        
        print(f"\nTasks in conversation ({len(result.tasks)}):")
        for task in result.tasks:
            print(f"  - {task.title} [{task.status}]")
            
        print(f"\nMessages in conversation ({len(result.messages)}):")
        for message in result.messages:
            print(f"  - {message.role}: {message.content[:50]}...")


def main():
    """Main function to demonstrate the models."""
    print("Setting up database and creating sample data...")
    engine = create_db_and_tables()
    create_sample_data(engine)
    
    print("\nThe models have been successfully demonstrated!")


if __name__ == "__main__":
    main()