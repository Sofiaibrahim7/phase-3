<<<<<<< HEAD
# Qwen Code Project

This project contains implementations for task, conversation, and message models using SQLModel, an OpenAI Agent for intelligent task management, and a stateless chat API endpoint.

## Database Models

### Task, Conversation, and Message Models

SQLModel models for managing tasks, conversations, and messages with proper relationships and timestamps.

#### Models Overview

##### Task Model
- `id`: Unique identifier
- `title`: Task title (indexed)
- `description`: Task description
- `status`: Task status (pending, in_progress, completed, cancelled)
- `priority`: Priority level (low, medium, high, urgent)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `conversation_id`: Foreign key linking to a conversation (optional)

##### Conversation Model
- `id`: Unique identifier
- `title`: Conversation title (indexed)
- `description`: Conversation description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `messages`: Related messages (one-to-many relationship)
- `tasks`: Related tasks (one-to-many relationship)

##### Message Model
- `id`: Unique identifier
- `content`: Message content
- `role`: Sender role (user, assistant, system)
- `timestamp`: Message timestamp
- `created_at`: Record creation timestamp
- `updated_at`: Record last update timestamp
- `conversation_id`: Foreign key linking to a conversation

#### Features

- **Timestamps**: All models include `created_at` and `updated_at` fields
- **Relationships**: Properly defined relationships between models
- **Validation**: Field validations using Pydantic
- **Enums**: Type-safe enums for status, priority, and role fields
- **Cascading**: Proper cascading behavior for related records

## OpenAI Agent

An intelligent chatbot that interprets user natural language, selects appropriate MCP tools, confirms actions politely, and handles errors gracefully.

### Features

- **Natural Language Processing**: Interprets user requests expressed in natural language
- **MCP Tool Selection**: Identifies the most appropriate tools for each request
- **Action Confirmation**: Politely confirms sensitive operations before executing
- **Error Handling**: Gracefully handles cases where requested tasks are not found

### Supported Operations

- `create_task`: Create a new task with title, description, and status
- `update_task`: Update an existing task's properties
- `delete_task`: Delete a task (requires confirmation)
- `get_task`: Retrieve details of a specific task
- `list_tasks`: List all tasks or filter by status
- `create_conversation`: Create a new conversation
- `add_message`: Add a message to a conversation
- `get_conversation`: Retrieve details of a specific conversation

## Chat API Endpoint

A stateless REST API endpoint that processes user messages and persists conversation history in the database.

### Endpoints

- `POST /api/{user_id}/chat`: Process user messages and maintain conversation history
- `GET /api/conversations/{conversation_id}`: Retrieve conversation details
- `GET /api/users/{user_id}/conversations`: Retrieve all conversations for a user

### Features

- **Stateless Operation**: No in-memory state between requests
- **Database Persistence**: Conversation history stored in database
- **Request Validation**: Proper validation of user inputs
- **Error Handling**: Comprehensive error responses
- **Integration**: Connects with OpenAI Agent for message processing

## Usage

### Database Models

```python
from sqlmodel import SQLModel, create_engine, Session
from models.database_models import Task, Conversation, Message

# Create database and tables
engine = create_engine("sqlite:///example.db")
SQLModel.metadata.create_all(engine)

# Create a conversation
with Session(engine) as session:
    conversation = Conversation(
        title="Project Discussion",
        description="Planning the new project"
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Create a task linked to the conversation
    task = Task(
        title="Design database schema",
        conversation_id=conversation.id
    )
    session.add(task)
    session.commit()
```

### OpenAI Agent

```python
import asyncio
from agent.openai_agent import OpenAIAgent

async def main():
    # Initialize the agent with your OpenAI API key
    agent = OpenAIAgent(api_key="your-openai-api-key")

    # Process a user request
    response = await agent.handle_user_request("Create a task to implement user authentication")
    print(response)

asyncio.run(main())
```

### Chat API

To run the API server:
```bash
uvicorn api.chat_endpoint:app --reload
```

## Running Examples

### Database Models
To run the database model examples:

```bash
python example_usage.py
```

This will create a SQLite database and demonstrate the models in action.

### OpenAI Agent
To run the agent examples:

```bash
python example_agent.py
```

To run the tests:

```bash
python test_agent.py
```

### API Verification
To verify the API implementation:

```bash
python verify_api.py
```

## File Structure

- `@specs/database/schema.md`: Database schema specification
- `@specs/features/chatbot.md`: Chatbot feature specification
- `@specs/api/chat-endpoint.md`: Chat API endpoint specification
- `models/database_models.py`: SQLModel implementations
- `agent/openai_agent.py`: OpenAI Agent implementation
- `api/chat_endpoint.py`: Chat API endpoint implementation
- `example_usage.py`: Database model usage examples
- `example_agent.py`: Agent functionality demonstration
- `test_agent.py`: Agent tests
- `verify_api.py`: API verification script
- `API_DOCUMENTATION.md`: Complete API documentation
=======
# phase-3
>>>>>>> 67eca1bc572069da5ea8ae05333a85aea140b615
