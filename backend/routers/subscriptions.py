from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta
import os
import requests

from database import get_db, User, Subscription, SubscriptionPlan
from utils.security import verify_token, sanitize_input

router = APIRouter()
security = HTTPBearer()

# Flutterwave configuration
FLUTTERWAVE_SECRET_KEY = os.getenv("FLUTTERWAVE_SECRET_KEY")
FLUTTERWAVE_PUBLIC_KEY = os.getenv("FLUTTERWAVE_PUBLIC_KEY")

# Subscription plans configuration
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "currency": "USD",
        "duration_days": 30,
        "features": [
            "100 messages per month",
            "5 AI rules",
            "Basic analytics",
            "Email support"
        ]
    },
    "basic": {
        "name": "Basic",
        "price": 29.99,
        "currency": "USD",
        "duration_days": 30,
        "features": [
            "1,000 messages per month",
            "25 AI rules",
            "Advanced analytics",
            "Priority support",
            "Custom branding"
        ]
    },
    "pro": {
        "name": "Professional",
        "price": 99.99,
        "currency": "USD",
        "duration_days": 30,
        "features": [
            "10,000 messages per month",
            "100 AI rules",
            "Real-time analytics",
            "24/7 support",
            "API access",
            "Multi-platform integration"
        ]
    },
    "enterprise": {
        "name": "Enterprise",
        "price": 299.99,
        "currency": "USD",
        "duration_days": 30,
        "features": [
            "Unlimited messages",
            "Unlimited AI rules",
            "Custom analytics",
            "Dedicated support",
            "Advanced API access",
            "White-label options",
            "Custom integrations"
        ]
    }
}

# Pydantic models
class SubscriptionPlanResponse(BaseModel):
    plan_id: str
    name: str
    price: float
    currency: str
    duration_days: int
    features: List[str]

class PaymentRequest(BaseModel):
    plan_id: str
    email: str
    amount: float
    currency: str = "USD"
    redirect_url: Optional[str] = None

class PaymentResponse(BaseModel):
    payment_link: str
    reference: str

class SubscriptionResponse(BaseModel):
    id: int
    plan: str
    amount: float
    currency: str
    status: str
    started_at: str
    expires_at: Optional[str]
    flutterwave_reference: Optional[str]
    
    class Config:
        from_attributes = True

@router.get("/plans", response_model=List[SubscriptionPlanResponse])
async def get_subscription_plans():
    """Get available subscription plans."""
    
    plans = []
    for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
        plans.append(SubscriptionPlanResponse(
            plan_id=plan_id,
            name=plan_data["name"],
            price=plan_data["price"],
            currency=plan_data["currency"],
            duration_days=plan_data["duration_days"],
            features=plan_data["features"]
        ))
    
    return plans

@router.post("/initiate-payment", response_model=PaymentResponse)
async def initiate_payment(
    payment_data: PaymentRequest,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Initiate payment for subscription upgrade."""
    
    if not FLUTTERWAVE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service not configured"
        )
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Validate plan
    if payment_data.plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid subscription plan"
        )
    
    plan = SUBSCRIPTION_PLANS[payment_data.plan_id]
    
    # Create payment request to Flutterwave
    payment_data_flutter = {
        "tx_ref": f"chatpulse_{user.id}_{datetime.utcnow().timestamp()}",
        "amount": str(payment_data.amount),
        "currency": payment_data.currency,
        "redirect_url": payment_data.redirect_url or "https://yourapp.com/payment/success",
        "payment_options": "card, banktransfer, ussd",
        "customer": {
            "email": payment_data.email,
            "name": user.full_name or user.username
        },
        "customizations": {
            "title": f"ChatPulse {plan['name']} Plan",
            "description": f"Subscribe to {plan['name']} plan",
            "logo": "https://yourapp.com/logo.png"
        }
    }
    
    try:
        response = requests.post(
            "https://api.flutterwave.com/v3/payments",
            json=payment_data_flutter,
            headers={
                "Authorization": f"Bearer {FLUTTERWAVE_SECRET_KEY}",
                "Content-Type": "application/json"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Payment service error"
            )
        
        payment_response = response.json()
        
        if payment_response.get("status") != "success":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment initiation failed"
            )
        
        return PaymentResponse(
            payment_link=payment_response["data"]["link"],
            reference=payment_response["data"]["tx_ref"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment service error: {str(e)}"
        )

@router.get("/current", response_model=SubscriptionResponse)
async def get_current_subscription(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's current subscription."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Get active subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        # Create free subscription if none exists
        subscription = Subscription(
            user_id=user.id,
            plan=SubscriptionPlan.FREE,
            amount=0,
            currency="USD",
            status="active",
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return {
        "id": subscription.id,
        "plan": subscription.plan.value,
        "amount": subscription.amount,
        "currency": subscription.currency,
        "status": subscription.status,
        "started_at": subscription.started_at.isoformat(),
        "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
        "flutterwave_reference": subscription.flutterwave_reference
    }

@router.get("/history", response_model=List[SubscriptionResponse])
async def get_subscription_history(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get user's subscription history."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    subscriptions = db.query(Subscription).filter(
        Subscription.user_id == user.id
    ).order_by(Subscription.created_at.desc()).all()
    
    return [
        {
            "id": sub.id,
            "plan": sub.plan.value,
            "amount": sub.amount,
            "currency": sub.currency,
            "status": sub.status,
            "started_at": sub.started_at.isoformat(),
            "expires_at": sub.expires_at.isoformat() if sub.expires_at else None,
            "flutterwave_reference": sub.flutterwave_reference
        }
        for sub in subscriptions
    ]

@router.post("/cancel")
async def cancel_subscription(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Cancel current subscription (will expire at end of period)."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Get active subscription
    subscription = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    if subscription.plan == SubscriptionPlan.FREE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel free subscription"
        )
    
    # Mark as cancelled (will expire naturally)
    subscription.status = "cancelled"
    db.commit()
    
    return {"message": "Subscription cancelled successfully"}

@router.get("/usage")
async def get_subscription_usage(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Get subscription usage statistics."""
    
    payload = verify_token(credentials.credentials)
    email = payload.get("sub")
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Get current month's message count
    from database import ChatMessage, ChatSession
    
    current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    message_count = db.query(ChatMessage).join(ChatSession).filter(
        ChatSession.user_id == user.id,
        ChatMessage.created_at >= current_month_start
    ).count()
    
    # Get limits based on plan
    plan_limits = {
        "free": 100,
        "basic": 1000,
        "pro": 10000,
        "enterprise": -1  # Unlimited
    }
    
    limit = plan_limits.get(user.subscription_plan.value, 100)
    
    return {
        "current_plan": user.subscription_plan.value,
        "messages_used": message_count,
        "messages_limit": limit,
        "messages_remaining": max(0, limit - message_count) if limit > 0 else "Unlimited",
        "reset_date": (current_month_start + timedelta(days=32)).replace(day=1).isoformat()
    }
