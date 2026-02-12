# Chat Endpoint API Specification

## Overview
Implements a stateless chat endpoint that persists conversation history in the database.

## Endpoint
`POST /api/{user_id}/chat`

## Path Parameters
- `user_id` (string): Unique identifier for the user

## Request Body
```json
{
  "message": "User's message content",
  "conversation_id": "Optional conversation ID to continue existing conversation"
}
```

## Response
### Success Response (200 OK)
```json
{
  "conversation_id": "ID of the conversation",
  "response": "Assistant's response",
  "timestamp": "ISO 8601 timestamp"
}
```

### Error Responses
- `400 Bad Request`: Invalid request body
- `404 Not Found`: User or conversation not found
- `500 Internal Server Error`: Server error

## Requirements

### Stateless Server
- The server must not maintain in-memory state between requests
- All conversation state must be persisted in the database
- Each request should load necessary data from the database

### Conversation Persistence
- Conversation history must be stored in the database
- Each user can have multiple conversations
- Messages within conversations must be ordered chronologically
- Conversation metadata (title, creation date, etc.) should be maintained

### Security
- Validate user_id parameter to prevent injection attacks
- Sanitize all user inputs
- Implement rate limiting to prevent abuse

## Implementation Notes
- Use the existing Task, Conversation, and Message models
- Integrate with the OpenAI Agent for processing user messages
- Ensure proper database transactions for data consistency
