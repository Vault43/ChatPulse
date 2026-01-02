from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from database import get_db, User, APIKey
from utils.security import verify_token, generate_api_key, sanitize_input

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class UserProfile(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None

class APIKeyCreate(BaseModel):
    key_name: str

class APIKeyResponse(BaseModel):
    id: int
    key_name: str
    api_key: str
    is_active: bool
    last_used: Optional[str] = None
    created_at: str
    
    class Config:
        from_attributes = True

@router.get("/profile")
async def get_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user profile information."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "phone": user.phone,
        "company": user.company,
        "subscription_plan": user.subscription_plan.value,
        "subscription_status": user.subscription_status,
        "is_verified": user.is_verified,
        "status": user.status.value,
        "created_at": user.created_at.isoformat()
    }

@router.put("/profile")
async def update_user_profile(
    profile: UserProfile,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update user profile information."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Update profile fields
    if profile.full_name is not None:
        user.full_name = sanitize_input(profile.full_name)
    if profile.phone is not None:
        user.phone = sanitize_input(profile.phone)
    if profile.company is not None:
        user.company = sanitize_input(profile.company)
    
    db.commit()
    
    return {"message": "Profile updated successfully"}

@router.get("/api-keys", response_model=List[APIKeyResponse])
async def get_api_keys(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's API keys."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    api_keys = db.query(APIKey).filter(APIKey.user_id == user.id).all()
    
    return [
        {
            "id": key.id,
            "key_name": key.key_name,
            "api_key": key.api_key,
            "is_active": key.is_active,
            "last_used": key.last_used.isoformat() if key.last_used else None,
            "created_at": key.created_at.isoformat()
        }
        for key in api_keys
    ]

@router.post("/api-keys", response_model=APIKeyResponse)
async def create_api_key(
    key_data: APIKeyCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new API key."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate API key
    api_key = generate_api_key()
    
    # Create API key record
    db_api_key = APIKey(
        user_id=user.id,
        key_name=sanitize_input(key_data.key_name),
        api_key=api_key
    )
    
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    
    return {
        "id": db_api_key.id,
        "key_name": db_api_key.key_name,
        "api_key": db_api_key.api_key,
        "is_active": db_api_key.is_active,
        "last_used": None,
        "created_at": db_api_key.created_at.isoformat()
    }

@router.delete("/api-keys/{key_id}")
async def delete_api_key(
    key_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete an API key."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Find and delete API key
    api_key = db.query(APIKey).filter(
        APIKey.id == key_id,
        APIKey.user_id == user.id
    ).first()
    
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found"
        )
    
    db.delete(api_key)
    db.commit()
    
    return {"message": "API key deleted successfully"}

@router.get("/stats")
async def get_user_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user statistics."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Get user's chat sessions count
    from database import ChatSession, ChatMessage, AIRule
    
    chat_sessions = db.query(ChatSession).filter(ChatSession.user_id == user.id).count()
    chat_messages = db.query(ChatMessage).join(ChatSession).filter(ChatSession.user_id == user.id).count()
    ai_rules = db.query(AIRule).filter(AIRule.user_id == user.id).count()
    
    return {
        "chat_sessions": chat_sessions,
        "total_messages": chat_messages,
        "ai_rules": ai_rules,
        "subscription_plan": user.subscription_plan.value,
        "subscription_status": user.subscription_status
    }
