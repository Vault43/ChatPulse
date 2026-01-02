from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid
import json

from database import get_db, User, ChatSession, ChatMessage
from utils.security import verify_token, sanitize_input

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class ChatMessageCreate(BaseModel):
    session_id: str
    content: str
    message_type: str = "customer"  # customer, ai, human
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    platform: Optional[str] = "website"

class ChatMessageResponse(BaseModel):
    id: int
    session_id: int
    message_type: str
    content: str
    created_at: str
    
    class Config:
        from_attributes = True

class ChatSessionCreate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    platform: str = "website"

class ChatSessionResponse(BaseModel):
    id: int
    session_id: str
    customer_name: Optional[str]
    customer_email: Optional[str]
    customer_phone: Optional[str]
    platform: str
    status: str
    created_at: str
    updated_at: str
    message_count: int
    
    class Config:
        from_attributes = True

@router.post("/sessions", response_model=ChatSessionResponse)
async def create_chat_session(
    session_data: ChatSessionCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new chat session."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate unique session ID
    session_uuid = str(uuid.uuid4())
    
    # Create chat session
    db_session = ChatSession(
        user_id=user.id,
        session_id=session_uuid,
        customer_name=sanitize_input(session_data.customer_name) if session_data.customer_name else None,
        customer_email=sanitize_input(session_data.customer_email) if session_data.customer_email else None,
        customer_phone=sanitize_input(session_data.customer_phone) if session_data.customer_phone else None,
        platform=sanitize_input(session_data.platform)
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return {
        "id": db_session.id,
        "session_id": db_session.session_id,
        "customer_name": db_session.customer_name,
        "customer_email": db_session.customer_email,
        "customer_phone": db_session.customer_phone,
        "platform": db_session.platform,
        "status": db_session.status,
        "created_at": db_session.created_at.isoformat(),
        "updated_at": db_session.updated_at.isoformat(),
        "message_count": 0
    }

@router.get("/sessions", response_model=List[ChatSessionResponse])
async def get_chat_sessions(
    skip: int = 0,
    limit: int = 50,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's chat sessions."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Get sessions with message count
    sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).offset(skip).limit(limit).all()
    
    result = []
    for session in sessions:
        message_count = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).count()
        
        result.append({
            "id": session.id,
            "session_id": session.session_id,
            "customer_name": session.customer_name,
            "customer_email": session.customer_email,
            "customer_phone": session.customer_phone,
            "platform": session.platform,
            "status": session.status,
            "created_at": session.created_at.isoformat(),
            "updated_at": session.updated_at.isoformat(),
            "message_count": message_count
        })
    
    return result

@router.get("/sessions/{session_id}/messages", response_model=List[ChatMessageResponse])
async def get_chat_messages(
    session_id: str,
    skip: int = 0,
    limit: int = 100,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get messages for a specific chat session."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Find session
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Get messages
    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).offset(skip).limit(limit).all()
    
    return [
        {
            "id": msg.id,
            "session_id": msg.session_id,
            "message_type": msg.message_type,
            "content": msg.content,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]

@router.post("/messages", response_model=ChatMessageResponse)
async def create_chat_message(
    message_data: ChatMessageCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new chat message."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Find session
    session = db.query(ChatSession).filter(
        ChatSession.session_id == message_data.session_id,
        ChatSession.user_id == user.id
    ).first()
    
    if not session:
        # Create session if it doesn't exist
        session = ChatSession(
            user_id=user.id,
            session_id=message_data.session_id,
            customer_name=sanitize_input(message_data.customer_name) if message_data.customer_name else None,
            customer_email=sanitize_input(message_data.customer_email) if message_data.customer_email else None,
            customer_phone=sanitize_input(message_data.customer_phone) if message_data.customer_phone else None,
            platform=sanitize_input(message_data.platform) if message_data.platform else "website"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
    
    # Create message
    db_message = ChatMessage(
        session_id=session.id,
        message_type=message_data.message_type,
        content=sanitize_input(message_data.content)
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return {
        "id": db_message.id,
        "session_id": db_message.session_id,
        "message_type": db_message.message_type,
        "content": db_message.content,
        "created_at": db_message.created_at.isoformat()
    }

@router.delete("/sessions/{session_id}")
async def delete_chat_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete a chat session and its messages."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Find session
    session = db.query(ChatSession).filter(
        ChatSession.session_id == session_id,
        ChatSession.user_id == user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )
    
    # Delete messages first
    db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
    
    # Delete session
    db.delete(session)
    db.commit()
    
    return {"message": "Chat session deleted successfully"}

@router.get("/analytics")
async def get_chat_analytics(
    days: int = 30,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get chat analytics for the user."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Get date range
    from datetime import timedelta
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get sessions in date range
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user.id,
        ChatSession.created_at >= start_date
    ).all()
    
    # Get messages in date range
    messages = db.query(ChatMessage).join(ChatSession).filter(
        ChatSession.user_id == user.id,
        ChatMessage.created_at >= start_date
    ).all()
    
    # Calculate analytics
    total_sessions = len(sessions)
    total_messages = len(messages)
    customer_messages = len([m for m in messages if m.message_type == "customer"])
    ai_messages = len([m for m in messages if m.message_type == "ai"])
    human_messages = len([m for m in messages if m.message_type == "human"])
    
    # Platform breakdown
    platforms = {}
    for session in sessions:
        platform = session.platform or "unknown"
        platforms[platform] = platforms.get(platform, 0) + 1
    
    return {
        "period_days": days,
        "total_sessions": total_sessions,
        "total_messages": total_messages,
        "customer_messages": customer_messages,
        "ai_messages": ai_messages,
        "human_messages": human_messages,
        "platforms": platforms,
        "average_messages_per_session": total_messages / total_sessions if total_sessions > 0 else 0
    }
