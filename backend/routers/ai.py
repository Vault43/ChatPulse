from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import json

from database import get_db, User, AIRule
from utils.security import verify_token, sanitize_input
from utils.ai_service import ai_service

router = APIRouter()
security = HTTPBearer()

# Pydantic models
class AIRuleCreate(BaseModel):
    name: str
    trigger_keywords: List[str]
    response_template: str
    priority: int = 1
    is_active: bool = True

class AIRuleUpdate(BaseModel):
    name: Optional[str] = None
    trigger_keywords: Optional[List[str]] = None
    response_template: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None

class AIRuleResponse(BaseModel):
    id: int
    name: str
    trigger_keywords: List[str]
    response_template: str
    is_active: bool
    priority: int
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class AIRequest(BaseModel):
    message: str
    session_context: Optional[List[dict]] = None
    provider: str = "openai"

class AIResponse(BaseModel):
    response: str
    provider: str
    rule_matched: Optional[str] = None

@router.post("/generate-response", response_model=AIResponse)
async def generate_ai_response(
    request: AIRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Generate AI response for a message."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check if user has AI access
    if user.subscription_plan.value == "free":
        # Free plan: limited responses per day
        pass  # Could implement daily limit check here
    
    # Generate response
    try:
        response = await ai_service.generate_response(
            message=sanitize_input(request.message),
            user_id=user.id,
            session_context=request.session_context,
            provider=request.provider
        )
        
        return AIResponse(
            response=response,
            provider=request.provider
        )
        
    except Exception as e:
        # Fallback response when AI service is unavailable
        print(f"AI Service Error: {e}")
        fallback_response = "I'm currently experiencing technical difficulties with my AI service. Please try again later or contact support if the issue persists."
        
        return AIResponse(
            response=fallback_response,
            provider="fallback"
        )

@router.get("/rules", response_model=List[AIRuleResponse])
async def get_ai_rules(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's AI rules."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    rules = db.query(AIRule).filter(AIRule.user_id == user.id).all()
    
    result = []
    for rule in rules:
        try:
            keywords = json.loads(rule.trigger_keywords) if rule.trigger_keywords else []
        except json.JSONDecodeError:
            keywords = []
        
        result.append({
            "id": rule.id,
            "name": rule.name,
            "trigger_keywords": keywords,
            "response_template": rule.response_template,
            "is_active": rule.is_active,
            "priority": rule.priority,
            "created_at": rule.created_at.isoformat(),
            "updated_at": rule.updated_at.isoformat()
        })
    
    return result

@router.post("/rules", response_model=AIRuleResponse)
async def create_ai_rule(
    rule_data: AIRuleCreate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Create a new AI rule."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Check rule limits based on subscription
    if user.subscription_plan.value == "free":
        existing_rules = db.query(AIRule).filter(AIRule.user_id == user.id).count()
        if existing_rules >= 5:  # Free plan limit
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Free plan limited to 5 AI rules"
            )
    
    # Create rule
    db_rule = AIRule(
        user_id=user.id,
        name=sanitize_input(rule_data.name),
        trigger_keywords=json.dumps(rule_data.trigger_keywords),
        response_template=sanitize_input(rule_data.response_template),
        priority=rule_data.priority,
        is_active=rule_data.is_active
    )
    
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    
    return {
        "id": db_rule.id,
        "name": db_rule.name,
        "trigger_keywords": rule_data.trigger_keywords,
        "response_template": db_rule.response_template,
        "is_active": db_rule.is_active,
        "priority": db_rule.priority,
        "created_at": db_rule.created_at.isoformat(),
        "updated_at": db_rule.updated_at.isoformat()
    }

@router.put("/rules/{rule_id}", response_model=AIRuleResponse)
async def update_ai_rule(
    rule_id: int,
    rule_data: AIRuleUpdate,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Update an AI rule."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Find rule
    rule = db.query(AIRule).filter(
        AIRule.id == rule_id,
        AIRule.user_id == user.id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI rule not found"
        )
    
    # Update fields
    if rule_data.name is not None:
        rule.name = sanitize_input(rule_data.name)
    if rule_data.trigger_keywords is not None:
        rule.trigger_keywords = json.dumps(rule_data.trigger_keywords)
    if rule_data.response_template is not None:
        rule.response_template = sanitize_input(rule_data.response_template)
    if rule_data.priority is not None:
        rule.priority = rule_data.priority
    if rule_data.is_active is not None:
        rule.is_active = rule_data.is_active
    
    db.commit()
    db.refresh(rule)
    
    try:
        keywords = json.loads(rule.trigger_keywords) if rule.trigger_keywords else []
    except json.JSONDecodeError:
        keywords = []
    
    return {
        "id": rule.id,
        "name": rule.name,
        "trigger_keywords": keywords,
        "response_template": rule.response_template,
        "is_active": rule.is_active,
        "priority": rule.priority,
        "created_at": rule.created_at.isoformat(),
        "updated_at": rule.updated_at.isoformat()
    }

@router.delete("/rules/{rule_id}")
async def delete_ai_rule(
    rule_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Delete an AI rule."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Find and delete rule
    rule = db.query(AIRule).filter(
        AIRule.id == rule_id,
        AIRule.user_id == user.id
    ).first()
    
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="AI rule not found"
        )
    
    db.delete(rule)
    db.commit()
    
    return {"message": "AI rule deleted successfully"}

@router.get("/providers")
async def get_ai_providers(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Get available AI providers."""
    
    verify_token(credentials.credentials)  # Just verify authentication
    
    providers = ai_service.get_supported_providers()
    
    return {
        "providers": providers,
        "default": "openai"
    }

@router.get("/usage-stats")
async def get_ai_usage_stats(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get AI usage statistics."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Get AI rules count
    rules_count = db.query(AIRule).filter(AIRule.user_id == user.id).count()
    active_rules_count = db.query(AIRule).filter(
        AIRule.user_id == user.id,
        AIRule.is_active == True
    ).count()
    
    return {
        "total_rules": rules_count,
        "active_rules": active_rules_count,
        "subscription_plan": user.subscription_plan.value,
        "rules_limit": {
            "free": 5,
            "basic": 25,
            "pro": 100,
            "enterprise": -1  # Unlimited
        }.get(user.subscription_plan.value, 5)
    }
