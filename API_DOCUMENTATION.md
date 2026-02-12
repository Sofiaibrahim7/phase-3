# Chat API Endpoint Implementation

## Overview
Implements a stateless POST `/api/{user_id}/chat` endpoint that persists conversation history in the database.

## API Endpoints

### POST /api/{user_id}/chat
Processes user messages and maintains conversation history.

#### Path Parameters
- `user_id` (string): Unique identifier for the user

#### Request Body
```json
{
  "message": "User's message content",
  "conversation_id": "Optional conversation ID to continue existing conversation"
}
```

#### Response (200 OK)
```json
{
  "conversation_id": "ID of the conversation",
  "response": "Assistant's response",
  "timestamp": "ISO 8601 timestamp"
}
```

#### Error Responses
- `400 Bad Request`: Invalid request body
- `404 Not Found`: User or conversation not found
- `500 Internal Server Error`: Server error

### GET /api/conversations/{conversation_id}
Retrieves conversation details by ID.

### GET /api/users/{user_id}/conversations
Retrieves all conversations for a specific user.

## Implementation Details

### Stateless Design
- The server does not maintain in-memory state between requests
- All conversation state is loaded from the database for each request
- Each request is processed independently

### Database Persistence
- Conversation history is stored in the database using SQLModel
- Each conversation contains ordered messages
- Conversation metadata is maintained

### Integration with OpenAI Agent
- The endpoint integrates with the OpenAI Agent for processing user messages
- Natural language understanding and tool selection
- Action confirmation for sensitive operations
- Error handling for task-not-found scenarios

## File Structure
- `@specs/api/chat-endpoint.md`: API specification
- `api/chat_endpoint.py`: Main API implementation
- `models/database_models.py`: Database models (Conversation, Message)
- `agent/openai_agent.py`: OpenAI Agent integration

## Usage
To run the API server:
```bash
uvicorn api.chat_endpoint:app --reload
```

The server will be available at `http://localhost:8000`

## Key Features
- ✅ Stateless operation
- ✅ Conversation persistence in database
- ✅ Proper request validation
- ✅ Error handling
- ✅ Message ordering and retrieval
- ✅ Integration with OpenAI Agent
- ✅ Security measures (input validation)