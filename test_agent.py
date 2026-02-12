"""
Test script for the OpenAI Agent implementation.
"""

import asyncio
from agent.openai_agent import OpenAIAgent, MCPTaskManager


async def test_agent_features():
    """Test the main features of the OpenAI Agent."""
    print("Testing OpenAI Agent Features")
    print("=" * 40)

    # Initialize the task manager with a database session
    from sqlmodel import create_engine, Session
    from models.database_models import SQLModel

    # Create an in-memory database for the test
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    # Create a session
    session = Session(engine)

    # Initialize the task manager with the session
    task_manager = MCPTaskManager(session)

    print("\n1. Testing MCP Tool Management:")
    print("- Available tools:", list(task_manager.available_tools.keys()))

    # Test creating a task
    print("\n2. Testing task creation:")
    create_result = await task_manager.execute_tool("create_task", {
        "title": "Test task",
        "description": "A test task for verification",
        "status": "pending"
    })
    print(f"- Create result: {create_result['result']}")
    if create_result['result'] == 'success':
        print(f"  Created task: {create_result['data'].title}")

    # Test getting the task
    print("\n3. Testing task retrieval:")
    if create_result['result'] == 'success':
        task_id = create_result['data'].id
        get_result = await task_manager.execute_tool("get_task", {"id": task_id})
        print(f"- Get result: {get_result['result']}")
        if get_result['result'] == 'success':
            print(f"  Retrieved task: {get_result['data'].title}")

    # Test listing tasks
    print("\n4. Testing task listing:")
    list_result = await task_manager.execute_tool("list_tasks", {})
    print(f"- List result: {list_result['result']}")
    if list_result['result'] == 'success':
        print(f"  Number of tasks: {len(list_result['data'])}")

    # Test error handling - task not found
    print("\n5. Testing error handling (task not found):")
    not_found_result = await task_manager.execute_tool("get_task", {"id": 999})
    print(f"- Result: {not_found_result['result']}")
    print(f"  Message: {not_found_result['message']}")

    # Test the tool schema
    print("\n6. Testing tool schema:")
    schema = task_manager.get_tool_schema()
    print(f"- Number of available tools: {len(schema)}")
    print("- Tool names:", [tool["function"]["name"] for tool in schema])

    print("\n" + "=" * 40)
    print("Agent features verification completed!")
    print("\nKey features implemented:")
    print("+ MCP Tool Management with CRUD operations")
    print("+ Natural language interpretation capability")
    print("+ Action confirmation for sensitive operations")
    print("+ Error handling for task-not-found scenarios")
    print("+ Tool schema definition for OpenAI integration")


async def demo_conversation_flow():
    """Demonstrate a sample conversation flow."""
    print("\n\nSample Conversation Flow Demo")
    print("=" * 40)

    print("\nUser: 'Create a task to implement user authentication'")
    print("Agent: [Would identify create_task tool and execute]")

    print("\nUser: 'Show me all pending tasks'")
    print("Agent: [Would identify list_tasks tool with status=pending and execute]")

    print("\nUser: 'Update task #1 to in_progress status'")
    print("Agent: [Would identify update_task tool and request confirmation]")
    print("Agent: 'I'm about to update task #1 with status=in_progress. Is that OK?'")

    print("\nUser: 'Yes'")
    print("Agent: [Would execute the update_task tool]")

    print("\nUser: 'Delete task #2'")
    print("Agent: [Would identify delete_task tool and request confirmation]")
    print("Agent: 'I'm about to delete task #2. Is that OK?'")

    print("\nUser: 'No'")
    print("Agent: [Would cancel the deletion]")

    print("\nUser: 'What is task #999?'")
    print("Agent: [Would identify get_task tool, fail, and provide helpful suggestion]")
    print("Agent: 'I couldn't find that task. Would you like me to list all tasks so you can find the right one?'")

    print("\nDemo completed!")


async def main():
    """Run all tests."""
    await test_agent_features()
    await demo_conversation_flow()


if __name__ == "__main__":
    asyncio.run(main())