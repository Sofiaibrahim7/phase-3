# Phase III Todo AI Chatbot

A stateless AI chatbot application that integrates FastAPI, SQLModel, OpenAI Agents SDK, and MCP SDK for intelligent task management.

## Features

- **Stateless Architecture**: No in-memory state between requests; all data persisted in database
- **Natural Language Processing**: Understands user requests in natural language
- **Task Management**: Create, update, delete, and view tasks with status and priority
- **Conversation History**: Maintains conversation history in database
- **MCP Tool Integration**: Integrates with MCP tools for extended functionality
- **OpenAI Agent**: Uses OpenAI's API for intelligent responses

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLModel**: SQL databases with Python types for data validation
- **OpenAI Agents SDK**: For intelligent natural language processing
- **MCP SDK**: For integrating with MCP tools
- **ChatKit Frontend**: User-friendly chat interface (to be integrated)

## Architecture

### Database Models
- **Task**: Represents individual tasks with title, description, status, and priority
- **Conversation**: Groups related messages together
- **Message**: Individual messages within conversations

### API Endpoints
- `POST /api/{user_id}/chat`: Process user messages and maintain conversation history
- `GET /api/conversations/{conversation_id}`: Retrieve conversation details
- `GET /api/users/{user_id}/conversations`: Retrieve all conversations for a user
- `GET /api/tasks`: Retrieve all tasks with optional status filtering

## Setup

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set environment variables:
   ```bash
   export OPENAI_API_KEY='your-openai-api-key'
   export DATABASE_URL='sqlite:///chat_app.db'  # or your preferred database
   ```

### Running the Application

#### Using the startup script:
```bash
# On Unix/Linux/MacOS
./start.sh

# On Windows
start.bat
```

#### Or run directly:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at `http://localhost:8000`

## Usage Examples

### Creating a Task
User: "Create a task to implement user authentication"
Agent: "I've created a task: 'Implement user authentication' with status 'pending'"

### Updating a Task
User: "Update task #1 to in_progress status"
Agent: "I'm about to update task #1 to 'in_progress' status. Is that OK?"

### Listing Tasks
User: "Show me all pending tasks"
Agent: "Here are your pending tasks: [list of tasks]"

### Deleting a Task
User: "Delete task #2"
Agent: "I'm about to delete task #2. Is that OK?"

## API Documentation

Once the server is running, visit `http://localhost:8000/docs` for interactive API documentation.

## Database Schema

The application uses SQLModel to define the following database schema:

### Task Model
- `id`: Unique identifier
- `title`: Task title (indexed)
- `description`: Task description
- `status`: Task status (pending, in_progress, completed, cancelled)
- `priority`: Priority level (low, medium, high, urgent)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `conversation_id`: Foreign key linking to a conversation (optional)

### Conversation Model
- `id`: Unique identifier
- `title`: Conversation title (indexed)
- `description`: Conversation description
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `messages`: Related messages (one-to-many relationship)
- `tasks`: Related tasks (one-to-many relationship)

### Message Model
- `id`: Unique identifier
- `content`: Message content
- `role`: Sender role (user, assistant, system)
- `timestamp`: Message timestamp
- `created_at`: Record creation timestamp
- `updated_at`: Record last update timestamp
- `conversation_id`: Foreign key linking to a conversation

## Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `DATABASE_URL`: Database connection string (defaults to sqlite:///chat_app.db)

## Error Handling

The application handles various error scenarios:
- Invalid user input
- Non-existent tasks or conversations
- Database connection issues
- OpenAI API errors

## Security

- Input validation on all endpoints
- Parameter sanitization
- Secure database connections
- Rate limiting (to be implemented)

## MCP SDK Integration

The application is designed to integrate with MCP (Model Context Protocol) SDK for extended functionality. The current implementation includes placeholder methods that can be expanded to connect with actual MCP tools.

## ChatKit Frontend Integration

The backend is designed to work with ChatKit frontend for a complete user experience. The API endpoints are structured to support real-time chat functionality.

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Code Formatting
```bash
black .
```

### Linting
```bash
flake8 .
```

## Deployment

For production deployment:
1. Use a production-ready database (PostgreSQL, MySQL)
2. Set up proper authentication
3. Implement rate limiting
4. Add monitoring and logging
5. Use a WSGI/ASGI server like Gunicorn

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License