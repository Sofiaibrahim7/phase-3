"""
Chat API endpoint implementation.

Implements a stateless POST /api/{user_id}/chat endpoint that persists 
conversation history in the database.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Session, create_engine, select
from contextlib import asynccontextmanager
import asyncio
import os
from unittest.mock import MagicMock


from models.database_models import Conversation, Message, RoleType
from agent.openai_agent import OpenAIAgent, MCPTaskManager


# Pydantic models for request/response
class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    conversation_id: int
    response: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


# Global variables
engine = None
openai_agent = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global engine, openai_agent
    
    # Initialize database engine
    db_url = os.getenv("DATABASE_URL", "sqlite:///chat_app.db")
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)
    
    # Initialize OpenAI agent with a mock client for this example
    # In a real implementation, you would use the real OpenAI API
    # openai_agent = OpenAIAgent(api_key=os.getenv("OPENAI_API_KEY"))
    
    yield
    
    # Cleanup
    if engine:
        engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Chat API",
    description="Stateless chat API endpoint with database persistence",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session


def get_mock_openai_agent():
    """Get or create a mock OpenAI agent instance for this example."""
    # Since we don't have an actual OpenAI API key in this example,
    # we'll create a mock agent that simulates the behavior
    class MockOpenAIAgent:
        async def handle_user_request(self, user_input: str, confirm_actions: bool = True) -> str:
            # Simulate processing the user input
            # In a real implementation, this would call the actual OpenAI API
            if "create" in user_input.lower() and "task" in user_input.lower():
                return f"I've created a task based on your request: '{user_input}'. This would normally connect to the task management system."
            elif "update" in user_input.lower() and "task" in user_input.lower():
                return f"I can help you update a task. For security, I would confirm this action before proceeding: '{user_input}'"
            elif "delete" in user_input.lower() and "task" in user_input.lower():
                return f"For security, I need to confirm before deleting any tasks. Are you sure you want to delete based on: '{user_input}'?"
            else:
                return f"I received your message: '{user_input}'. This is a simulated response from the OpenAI agent. In a real implementation, this would process your request using natural language understanding and execute appropriate tools."
    
    return MockOpenAIAgent()


@app.post(
    "/api/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse}
    }
)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    db_session: Session = Depends(get_db_session)
):
    """
    Chat endpoint that processes user messages and maintains conversation history.
    
    Args:
        user_id: Unique identifier for the user
        request: Chat request containing the message and optional conversation ID
        db_session: Database session dependency
    
    Returns:
        ChatResponse with conversation ID, response, and timestamp
    """
    try:
        # Validate user_id format (basic validation)
        if not user_id or len(user_id) < 1 or len(user_id) > 100:
            raise HTTPException(status_code=400, detail="Invalid user_id")
        
        # Validate message
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get or create conversation
        if request.conversation_id:
            # Try to get existing conversation
            conversation = db_session.get(Conversation, request.conversation_id)
            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            # Create new conversation
            conversation = Conversation(
                title=f"Conversation with {user_id}",
                description=f"Chat session for user {user_id}"
            )
            db_session.add(conversation)
            db_session.commit()
            db_session.refresh(conversation)
        
        # Add user message to conversation
        user_message = Message(
            content=request.message,
            role=RoleType.USER,
            conversation_id=conversation.id
        )
        db_session.add(user_message)
        db_session.commit()
        db_session.refresh(user_message)
        
        # Get the OpenAI agent (mock for this example)
        agent = get_mock_openai_agent()
        
        # Process the message with the OpenAI agent
        agent_response = await agent.handle_user_request(request.message)
        
        # Add assistant message to conversation
        assistant_message = Message(
            content=agent_response,
            role=RoleType.ASSISTANT,
            conversation_id=conversation.id
        )
        db_session.add(assistant_message)
        db_session.commit()
        
        # Return response
        return ChatResponse(
            conversation_id=conversation.id,
            response=agent_response,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error in a real implementation
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(
    conversation_id: int,
    db_session: Session = Depends(get_db_session)
):
    """
    Get conversation details by ID.
    
    Args:
        conversation_id: ID of the conversation to retrieve
        db_session: Database session dependency
    
    Returns:
        Conversation details with messages
    """
    try:
        conversation = db_session.get(Conversation, conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Load messages for this conversation
        statement = select(Message).where(Message.conversation_id == conversation_id).order_by(Message.timestamp)
        messages = db_session.exec(statement).all()
        
        return {
            "id": conversation.id,
            "title": conversation.title,
            "description": conversation.description,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "role": msg.role.value,
                    "timestamp": msg.timestamp.isoformat(),
                    "created_at": msg.created_at.isoformat()
                } for msg in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/users/{user_id}/conversations")
async def get_user_conversations(
    user_id: str,
    db_session: Session = Depends(get_db_session)
):
    """
    Get all conversations for a specific user.
    NOTE: In this implementation, we're not storing user IDs in the database,
    so this is a placeholder that would need to be enhanced with a User model.
    
    Args:
        user_id: ID of the user whose conversations to retrieve
        db_session: Database session dependency
    
    Returns:
        List of conversations for the user
    """
    try:
        # In a real implementation, you would have a way to associate conversations with users
        # For now, we'll return all conversations as a placeholder
        # This would be improved by adding a user_id field to the Conversation model
        statement = select(Conversation).order_by(Conversation.created_at.desc())
        conversations = db_session.exec(statement).all()
        
        return {
            "user_id": user_id,
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "description": conv.description,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                } for conv in conversations
            ]
        }
    except Exception as e:
        print(f"Error getting user conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {"message": "Chat API is running", "status": "ok"}


# For development/testing purposes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)