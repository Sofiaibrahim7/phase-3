# OpenAI Agent for Task Management

This project implements an OpenAI Agent that serves as an intelligent chatbot capable of interpreting user natural language, selecting appropriate MCP tools, confirming actions politely, and handling errors gracefully.

## Features

### Natural Language Processing
- Interprets user requests expressed in natural language
- Understands context and intent behind user queries
- Supports various ways of expressing the same request
- Maintains conversation context across multiple exchanges

### MCP Tool Selection
- Identifies the most appropriate MCP tool for each user request
- Maps user intents to specific tool capabilities
- Handles cases where multiple tools could be applicable
- Prioritizes tools based on relevance and efficiency

### Action Confirmation
- Politely confirms potentially destructive or important actions before executing
- Provides clear summaries of intended actions
- Allows users to approve, modify, or cancel pending actions
- Uses appropriate politeness markers and language

### Error Handling
- Gracefully handles cases where requested tasks are not found
- Provides helpful suggestions when tasks don't exist
- Offers alternatives when specific tools are unavailable
- Maintains conversation flow despite errors

## Architecture

### Components

1. **OpenAIAgent**: Main agent class that processes user requests and interacts with the OpenAI API
2. **MCPTaskManager**: Manages MCP tasks and their execution
3. **Tool Definitions**: JSON schemas defining available tools and their parameters
4. **Response Formatter**: Formats tool execution results into user-friendly messages

### Tool Functions

The agent supports the following MCP tools:

- `create_task`: Create a new task with title, description, and status
- `update_task`: Update an existing task's properties
- `delete_task`: Delete a task (requires confirmation)
- `get_task`: Retrieve details of a specific task
- `list_tasks`: List all tasks or filter by status
- `create_conversation`: Create a new conversation
- `add_message`: Add a message to a conversation
- `get_conversation`: Retrieve details of a specific conversation

## Usage

### Basic Usage

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

### With Confirmation

```python
# The agent will automatically request confirmation for sensitive operations
response = await agent.handle_user_request("Delete task #1")
print(response)  # Will ask for confirmation before deleting
```

## Implementation Details

### Natural Language Understanding
The agent uses OpenAI's function calling capability to map natural language requests to specific tool invocations. The system prompt guides the model to select appropriate tools based on user intent.

### Confirmation Logic
Certain operations (like deletions and updates) require explicit user confirmation to prevent accidental data loss. The agent identifies these operations and prompts the user before proceeding.

### Error Handling
When a requested task is not found, the agent provides helpful suggestions and alternatives rather than just returning an error. This improves the user experience by maintaining helpful conversation flow.

## Files

- `@specs/features/chatbot.md`: Feature specification document
- `agent/openai_agent.py`: Main implementation of the OpenAI Agent
- `example_agent.py`: Example demonstrating the agent's functionality
- `test_agent.py`: Test script verifying agent features

## Example Interactions

The agent can handle various types of requests:

- "Create a task to implement user authentication" → Creates a new task
- "Show me all pending tasks" → Lists tasks with pending status
- "Update task #1 to in_progress status" → Updates task with confirmation
- "Delete task #2" → Requests confirmation before deletion
- "What is task #999?" → Handles not-found error gracefully

## Running the Examples

To run the example demonstrations:

```bash
python example_agent.py
```

To run the tests:

```bash
python test_agent.py
```

## Dependencies

- openai>=1.0.0
- sqlmodel (for database models if using persistence)
- python-dotenv (for environment management, optional)

Install dependencies with:

```bash
pip install -r requirements.txt
```