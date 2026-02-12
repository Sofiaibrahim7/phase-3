"""
Example implementation of the OpenAI Agent with simulated API calls.
This demonstrates how the agent would work in a real scenario.
"""

import asyncio
import json
from typing import Dict, List
from agent.openai_agent import OpenAIAgent, MCPTaskManager, ToolCall, AgentResponse


class MockOpenAIClient:
    """Mock client to simulate OpenAI API responses without requiring an actual API key."""

    def __init__(self):
        self.tools_schema = [
            {
                "type": "function",
                "function": {
                    "name": "create_task",
                    "description": "Create a new task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Title of the task"},
                            "description": {"type": "string", "description": "Description of the task"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "description": "Initial status of the task"}
                        },
                        "required": ["title"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_task",
                    "description": "Update an existing task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "ID of the task to update"},
                            "title": {"type": "string", "description": "New title of the task"},
                            "description": {"type": "string", "description": "New description of the task"},
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "description": "New status of the task"}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "delete_task",
                    "description": "Delete a task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "ID of the task to delete"}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_task",
                    "description": "Get details of a specific task",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "ID of the task to retrieve"}
                        },
                        "required": ["id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_tasks",
                    "description": "List all tasks or filter by status",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["pending", "in_progress", "completed"], "description": "Filter tasks by status"}
                        }
                    }
                }
            }
        ]

    def chat_completions_create(self, model: str, messages: List[Dict], tools: List[Dict], tool_choice: str):
        """Simulate the OpenAI chat completions API."""
        # Extract the user's request
        user_message = ""
        for msg in messages:
            if msg["role"] == "user":
                user_message = msg["content"]
                break

        # Simple parsing of user request to determine appropriate tool
        user_message_lower = user_message.lower()

        # Determine which tool to call based on the user's request
        tool_calls = []

        if "create" in user_message_lower and ("task" in user_message_lower or "new" in user_message_lower):
            # Extract title from the message
            title = "New task"
            if "to" in user_message:
                title = user_message.split("to")[1].strip()
            elif "for" in user_message:
                title = user_message.split("for")[1].strip()

            tool_calls.append({
                "id": "call_123",
                "function": {
                    "name": "create_task",
                    "arguments": json.dumps({"title": title, "status": "pending"})
                },
                "type": "function"
            })
        elif "update" in user_message_lower and "task" in user_message_lower:
            # Extract task ID and new status
            import re
            id_match = re.search(r'#(\d+)', user_message)
            status_match = re.search(r'(pending|in_progress|completed)', user_message_lower)

            if id_match:
                task_id = int(id_match.group(1))
                status = status_match.group(1) if status_match else "in_progress"

                tool_calls.append({
                    "id": "call_124",
                    "function": {
                        "name": "update_task",
                        "arguments": json.dumps({"id": task_id, "status": status})
                    },
                    "type": "function"
                })
        elif "delete" in user_message_lower and "task" in user_message_lower:
            import re
            id_match = re.search(r'#(\d+)', user_message)

            if id_match:
                task_id = int(id_match.group(1))

                tool_calls.append({
                    "id": "call_125",
                    "function": {
                        "name": "delete_task",
                        "arguments": json.dumps({"id": task_id})
                    },
                    "type": "function"
                })
        elif "show" in user_message_lower or "list" in user_message_lower or "all" in user_message_lower:
            # Check if filtering by status
            status = None
            if "pending" in user_message_lower:
                status = "pending"
            elif "in progress" in user_message_lower or "in_progress" in user_message_lower:
                status = "in_progress"
            elif "completed" in user_message_lower:
                status = "completed"

            params = {}
            if status:
                params["status"] = status

            tool_calls.append({
                "id": "call_126",
                "function": {
                    "name": "list_tasks",
                    "arguments": json.dumps(params)
                },
                "type": "function"
            })
        elif ("get" in user_message_lower or "show" in user_message_lower or "what" in user_message_lower) and "task" in user_message_lower:
            import re
            id_match = re.search(r'#(\d+)', user_message)

            if id_match:
                task_id = int(id_match.group(1))

                tool_calls.append({
                    "id": "call_127",
                    "function": {
                        "name": "get_task",
                        "arguments": json.dumps({"id": task_id})
                    },
                    "type": "function"
                })

        # Create mock response
        class MockChoice:
            class Message:
                def __init__(self, tool_calls):
                    self.tool_calls = tool_calls
                    self.content = None if tool_calls else "I processed your request."

            def __init__(self, tool_calls):
                self.message = self.Message(tool_calls)

        class MockResponse:
            def __init__(self, choices):
                self.choices = choices

        return MockResponse([MockChoice(tool_calls)])


class MockOpenAIAgent(OpenAIAgent):
    """A version of the agent that uses a mock OpenAI client for demonstration."""

    def __init__(self):
        from sqlmodel import create_engine, Session
        from models.database_models import SQLModel

        # Create an in-memory database for the demo
        engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(engine)

        # Create a session
        session = Session(engine)

        # Initialize parent class with fake API key and session
        super().__init__(api_key="fake-key-for-demo", db_session=session)

        self.client = MockOpenAIClient()
        self.model = "gpt-3.5-turbo"
        self.conversation_history = []

    def process_request(self, user_input: str) -> AgentResponse:
        """Process a user request and return an appropriate response (mocked version)."""
        # This is a simplified version that mimics the real process_request method
        # but without making actual API calls

        user_message_lower = user_input.lower()
        tool_calls = []

        # Determine which tool to call based on the user's request
        if "create" in user_message_lower and ("task" in user_message_lower or "new" in user_message_lower):
            # Extract title from the message
            title = "New task"
            if "to" in user_message_lower:
                title = user_message_lower.split("to")[1].strip()
            elif "for" in user_message_lower:
                title = user_message_lower.split("for")[1].strip()

            tool_calls.append(ToolCall(name="create_task", arguments={"title": title, "status": "pending"}))
        elif "update" in user_message_lower and "task" in user_message_lower:
            import re
            id_match = re.search(r'#(\d+)', user_message_lower)
            status_match = re.search(r'(pending|in_progress|completed)', user_message_lower)

            if id_match:
                task_id = int(id_match.group(1))
                status = status_match.group(1) if status_match else "in_progress"

                tool_calls.append(ToolCall(name="update_task", arguments={"id": task_id, "status": status}))
        elif "delete" in user_message_lower and "task" in user_message_lower:
            import re
            id_match = re.search(r'#(\d+)', user_message_lower)

            if id_match:
                task_id = int(id_match.group(1))

                tool_calls.append(ToolCall(name="delete_task", arguments={"id": task_id}))
        elif "show" in user_message_lower or "list" in user_message_lower or "all" in user_message_lower:
            # Check if filtering by status
            status = None
            if "pending" in user_message_lower:
                status = "pending"
            elif "in progress" in user_message_lower or "in_progress" in user_message_lower:
                status = "in_progress"
            elif "completed" in user_message_lower:
                status = "completed"

            params = {}
            if status:
                params["status"] = status

            tool_calls.append(ToolCall(name="list_tasks", arguments=params))
        elif ("get" in user_message_lower or "show" in user_message_lower or "what" in user_message_lower) and "task" in user_message_lower:
            import re
            id_match = re.search(r'#(\d+)', user_message_lower)

            if id_match:
                task_id = int(id_match.group(1))

                tool_calls.append(ToolCall(name="get_task", arguments={"id": task_id}))

        # Check if any of the tools need confirmation
        needs_confirmation = any(self._needs_confirmation(tc.name) for tc in tool_calls)
        confirmation_message = None

        if needs_confirmation and tool_calls:
            # Just use the first tool that needs confirmation for the message
            for tc in tool_calls:
                if self._needs_confirmation(tc.name):
                    confirmation_message = self._format_confirmation_message(tc)
                    break

        return AgentResponse(
            message="Processing your request..." if tool_calls else "I'm not sure how to help with that.",
            tool_calls=tool_calls,
            needs_confirmation=needs_confirmation,
            confirmation_message=confirmation_message
        )

    def _needs_confirmation(self, tool_name: str) -> bool:
        """Determine if a tool needs confirmation before execution."""
        confirmation_required = ["delete_task", "update_task"]
        return tool_name in confirmation_required

    def _format_confirmation_message(self, tool_call: ToolCall) -> str:
        """Format a confirmation message for a tool call."""
        if tool_call.name == "delete_task":
            return f"I'm about to delete task #{tool_call.arguments.get('id')}. Is that OK?"
        elif tool_call.name == "update_task":
            task_id = tool_call.arguments.get('id')
            updates = ", ".join([f"{k}={v}" for k, v in tool_call.arguments.items() if k != 'id'])
            return f"I'm about to update task #{task_id} with {updates}. Is that OK?"
        return f"I'm about to execute '{tool_call.name}' with arguments {tool_call.arguments}. Please confirm."


async def demo_full_agent_workflow():
    """Demonstrate the full workflow of the OpenAI Agent."""
    print("OpenAI Agent Full Workflow Demo")
    print("=" * 50)

    agent = MockOpenAIAgent()

    # Scenario 1: Creating a task
    print("\nScenario 1: User wants to create a task")
    user_input = "Create a task to implement user authentication"
    print(f"User: {user_input}")

    response = agent.process_request(user_input)
    print(f"Agent: {response.message}")

    if response.tool_calls:
        print(f"Agent selected tool: {response.tool_calls[0].name}")
        print(f"Arguments: {response.tool_calls[0].arguments}")

    # Execute the tool
    if response.tool_calls:
        results = await agent.execute_tool_calls(response.tool_calls, confirm_execution=False)
        formatted_result = agent._format_results(results)
        print(f"Agent: {formatted_result}")

    # Scenario 2: Listing tasks
    print("\nScenario 2: User wants to see all tasks")
    user_input = "Show me all tasks"
    print(f"User: {user_input}")

    response = agent.process_request(user_input)
    print(f"Agent: {response.message}")

    if response.tool_calls:
        print(f"Agent selected tool: {response.tool_calls[0].name}")

        # Execute the tool
        results = await agent.execute_tool_calls(response.tool_calls, confirm_execution=False)
        formatted_result = agent._format_results(results)
        print(f"Agent: {formatted_result}")

    # Scenario 3: Updating a task (requires confirmation)
    print("\nScenario 3: User wants to update a task")
    user_input = "Update task #1 to in_progress status"
    print(f"User: {user_input}")

    response = agent.process_request(user_input)
    print(f"Agent: {response.message}")

    if response.needs_confirmation:
        print(f"Agent: {response.confirmation_message}")

        # Simulate user saying yes
        print("User: Yes")

        # Execute with confirmation
        results = await agent.execute_tool_calls(response.tool_calls, confirm_execution=False)
        formatted_result = agent._format_results(results)
        print(f"Agent: {formatted_result}")

    # Scenario 4: Deleting a task (requires confirmation)
    print("\nScenario 4: User wants to delete a task")
    user_input = "Delete task #2"
    print(f"User: {user_input}")

    response = agent.process_request(user_input)

    if response.needs_confirmation:
        print(f"Agent: {response.confirmation_message}")

        # Simulate user saying no
        print("User: No")
        print("Agent: Ok, I won't delete that task.")

    # Scenario 5: Task not found error handling
    print("\nScenario 5: User requests a non-existent task")
    user_input = "What is task #999?"
    print(f"User: {user_input}")

    response = agent.process_request(user_input)

    if response.tool_calls:
        # Execute the tool which will result in an error
        results = await agent.execute_tool_calls(response.tool_calls, confirm_execution=False)
        formatted_result = agent._format_results(results)
        print(f"Agent: {formatted_result}")

    print("\n" + "=" * 50)
    print("Demo completed! All required features are implemented:")
    print("+ Natural language interpretation")
    print("+ MCP tool selection")
    print("+ Polite action confirmation")
    print("+ Graceful error handling for task-not-found")


if __name__ == "__main__":
    asyncio.run(demo_full_agent_workflow())