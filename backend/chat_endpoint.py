from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from sqlmodel import Session, select
from backend.database import get_session, Conversation, Message
from backend.agent import OpenAIAgent


router = APIRouter()


class ChatRequest(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class ActionResponse(BaseModel):
    type: str  # task_created | task_updated | task_deleted | none
    task_id: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    action: ActionResponse
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    session: Session = Depends(get_session)
):
    """
    Stateless chat endpoint that persists conversation history in the database.
    """
    # Find or create conversation
    conversation = None
    if request.conversation_id:
        # Look for conversation by ID
        conversation = session.exec(
            select(Conversation).where(Conversation.id == int(request.conversation_id))
        ).first()

    if not conversation:
        # Create new conversation
        conversation = Conversation(
            title=request.message[:50],  # Use first 50 chars of message as title
            user_id=int(request.user_id)  # Using user_id directly without lookup
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

    # Save user message
    user_message = Message(
        content=request.message,
        role="user",
        conversation_id=conversation.id
    )
    session.add(user_message)

    # Process message with AI agent
    agent = OpenAIAgent()  # Initialize the agent
    ai_response = await agent.process_message(
        message=request.message,
        conversation_id=conversation.id,
        context=request.context
    )

    # Save AI response
    ai_message = Message(
        content=ai_response.response,
        role="assistant",
        conversation_id=conversation.id
    )
    session.add(ai_message)
    session.commit()

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    session.add(conversation)
    session.commit()

    return ChatResponse(
        conversation_id=str(conversation.id),
        response=ai_response.response,
        action=ActionResponse(
            type=ai_response.action_type,
            task_id=ai_response.task_id,
            details=ai_response.details
        ),
        timestamp=datetime.utcnow().isoformat()
    )