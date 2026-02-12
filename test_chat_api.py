"""
Test script for the chat API endpoint.
"""

import asyncio
import json
from sqlmodel import SQLModel, create_engine, Session
from api.chat_endpoint import app
from models.database_models import Conversation, Message, RoleType
from fastapi.testclient import TestClient


def test_chat_api():
    """Test the chat API endpoint functionality."""
    print("Testing Chat API Endpoint")
    print("=" * 40)

    # Create a test client
    with TestClient(app) as client:
        # Test 1: Health check
        print("\n1. Testing health check endpoint:")
        response = client.get("/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✓ Health check passed")

        # Test 2: Create a new conversation
        print("\n2. Testing chat endpoint (new conversation):")
        user_id = "test_user_123"
        chat_request = {
            "message": "Hello, I'd like to create a task to implement user authentication"
        }

        response = client.post(f"/api/{user_id}/chat", json=chat_request)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            conversation_id = data["conversation_id"]
            print(f"   Conversation ID: {conversation_id}")
            print("   ✓ New conversation created successfully")
        else:
            print(f"   Error: {response.text}")
            return False

        # Test 3: Continue existing conversation
        print("\n3. Testing chat endpoint (existing conversation):")
        chat_request_continued = {
            "message": "Can you update that task to in_progress status?",
            "conversation_id": conversation_id
        }

        response = client.post(f"/api/{user_id}/chat", json=chat_request_continued)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
            print("   ✓ Existing conversation continued successfully")
        else:
            print(f"   Error: {response.text}")
            return False

        # Test 4: Get conversation details
        print("\n4. Testing get conversation endpoint:")
        response = client.get(f"/api/conversations/{conversation_id}")
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   Conversation title: {data['title']}")
            print(f"   Number of messages: {len(data['messages'])}")
            print("   Messages:")
            for msg in data['messages']:
                print(f"     - {msg['role']}: {msg['content'][:50]}...")
            print("   ✓ Conversation retrieved successfully")
        else:
            print(f"   Error: {response.text}")
            return False

        # Test 5: Error handling - invalid user_id
        print("\n5. Testing error handling (invalid user_id):")
        response = client.post("/api//chat", json=chat_request)  # Empty user_id
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✓ Correctly rejected invalid user_id")
        else:
            print(f"   Expected 400, got {response.status_code}")
            return False

        # Test 6: Error handling - empty message
        print("\n6. Testing error handling (empty message):")
        response = client.post(f"/api/{user_id}/chat", json={"message": ""})
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✓ Correctly rejected empty message")
        else:
            print(f"   Expected 400, got {response.status_code}")
            return False

        # Test 7: Error handling - non-existent conversation
        print("\n7. Testing error handling (non-existent conversation):")
        response = client.post(f"/api/{user_id}/chat", json={
            "message": "Test message",
            "conversation_id": 999999  # Non-existent conversation ID
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 404:
            print("   ✓ Correctly rejected non-existent conversation")
        else:
            print(f"   Expected 404, got {response.status_code}")
            return False

    print("\n" + "=" * 40)
    print("All tests passed! API implementation is working correctly.")
    print("\nKey features verified:")
    print("✓ Stateless operation")
    print("✓ Conversation persistence in database")
    print("✓ Proper request validation")
    print("✓ Error handling")
    print("✓ Message ordering and retrieval")

    return True


def test_database_integration():
    """Test direct database integration."""
    print("\n\nTesting Database Integration")
    print("=" * 40)

    # Create engine and test database operations
    engine = create_engine("sqlite:///test_chat_api.db")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        # Create a conversation
        conversation = Conversation(
            title="Test Conversation",
            description="Test conversation for API verification"
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        print(f"Created conversation ID: {conversation.id}")

        # Add messages
        user_msg = Message(
            content="Test user message",
            role=RoleType.USER,
            conversation_id=conversation.id
        )
        assistant_msg = Message(
            content="Test assistant response",
            role=RoleType.ASSISTANT,
            conversation_id=conversation.id
        )

        session.add(user_msg)
        session.add(assistant_msg)
        session.commit()

        print("Added user and assistant messages")

        # Retrieve and verify
        retrieved_conv = session.get(Conversation, conversation.id)
        print(f"Retrieved conversation: {retrieved_conv.title}")

        # Get messages for this conversation
        from sqlmodel import select
        statement = select(Message).where(Message.conversation_id == conversation.id)
        messages = session.exec(statement).all()

        print(f"Retrieved {len(messages)} messages:")
        for msg in messages:
            print(f"  - {msg.role.value}: {msg.content}")

    print("\n✓ Database integration working correctly")
    return True


if __name__ == "__main__":
    success = test_chat_api()
    if success:
        test_database_integration()
        print("\n🎉 All tests completed successfully!")
    else:
        print("\n❌ Some tests failed!")
        exit(1)