"""
Phase III Todo AI Chatbot Application

This application integrates FastAPI, SQLModel, OpenAI Agents SDK, and MCP SDK
to create a stateless chatbot with database persistence.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Session, create_engine, select
from contextlib import asynccontextmanager
import os
import logging

from models.database_models import Conversation, Message, Task, RoleType, TaskStatus, PriorityLevel
from agent.openai_agent import OpenAIAgent


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global engine

    # Initialize database engine
    db_url = os.getenv("DATABASE_URL", "sqlite:///chat_app.db")
    engine = create_engine(db_url)
    SQLModel.metadata.create_all(engine)

    logger.info("Database initialized and tables created")

    yield

    # Cleanup
    if engine:
        engine.dispose()


# Create FastAPI app
app = FastAPI(
    title="Todo AI Chatbot",
    description="Phase III Todo AI Chatbot with MCP integration",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_session():
    """Dependency to get database session."""
    with Session(engine) as session:
        yield session


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
        conversation = None
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

        # Create an OpenAI agent instance with the current session
        api_key = os.getenv("OPENAI_API_KEY", "fake-key-for-demo")  # In production, use real API key
        agent = OpenAIAgent(api_key=api_key, db_session=db_session)

        # Process the message with the OpenAI agent
        agent_response = await agent.handle_user_request(request.message, db_session=db_session)

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
        # Log the error
        logger.error(f"Error in chat endpoint: {str(e)}")
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
        logger.error(f"Error getting conversation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/users/{user_id}/conversations")
async def get_user_conversations(
    user_id: str,
    db_session: Session = Depends(get_db_session)
):
    """
    Get all conversations for a specific user.

    Args:
        user_id: ID of the user whose conversations to retrieve
        db_session: Database session dependency

    Returns:
        List of conversations for the user
    """
    try:
        # In a real implementation, you would filter by user_id
        # For now, we'll return all conversations as a placeholder
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
        logger.error(f"Error getting user conversations: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/tasks")
async def get_tasks(
    status: Optional[str] = None,
    db_session: Session = Depends(get_db_session)
):
    """
    Get all tasks, optionally filtered by status.

    Args:
        status: Optional status to filter tasks
        db_session: Database session dependency

    Returns:
        List of tasks
    """
    try:
        statement = select(Task)
        if status:
            # Convert string status to enum if needed
            try:
                status_enum = TaskStatus(status)
                statement = statement.where(Task.status == status_enum)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status: {status}")

        tasks = db_session.exec(statement).all()

        return {
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status.value,
                    "priority": task.priority.value,
                    "created_at": task.created_at.isoformat(),
                    "updated_at": task.updated_at.isoformat(),
                    "conversation_id": task.conversation_id
                } for task in tasks
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "message": "Todo AI Chatbot is running",
        "status": "ok",
        "version": "1.0.0",
        "components": {
            "api": "available",
            "database": "connected",
            "openai_agent": "ready"
        }
    }


# For development/testing purposes
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
