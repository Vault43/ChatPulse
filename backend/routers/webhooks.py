from fastapi import APIRouter, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import hashlib
import hmac
import os
import json
from datetime import datetime, timedelta

from database import get_db, User, Subscription, SubscriptionPlan
from utils.security import sanitize_input

router = APIRouter()

# Flutterwave webhook secret
FLUTTERWAVE_SECRET_HASH = os.getenv("FLUTTERWAVE_SECRET_HASH")

class FlutterwaveWebhook(BaseModel):
    event: str
    data: dict

@router.post("/flutterwave")
async def flutterwave_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle Flutterwave payment webhooks."""
    
    if not FLUTTERWAVE_SECRET_HASH:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Webhook not configured"
        )
    
    # Get webhook signature
    signature = request.headers.get("verif-hash")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature"
        )
    
    # Get request body
    body = await request.body()
    
    # Verify signature
    expected_signature = hmac.new(
        FLUTTERWAVE_SECRET_HASH.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if signature != expected_signature:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )
    
    # Parse webhook data
    try:
        webhook_data = json.loads(body.decode())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON"
        )
    
    event = webhook_data.get("event")
    data = webhook_data.get("data", {})
    
    if event == "charge.completed":
        await handle_successful_payment(data, db)
    elif event == "payment.failed":
        await handle_failed_payment(data, db)
    
    return {"status": "received"}

async def handle_successful_payment(payment_data: dict, db: Session):
    """Handle successful payment."""
    
    try:
        # Extract payment information
        reference = payment_data.get("tx_ref", "")
        amount = float(payment_data.get("amount", 0))
        currency = payment_data.get("currency", "USD")
        customer_email = payment_data.get("customer", {}).get("email", "")
        
        # Extract user ID from reference (format: chatpulse_user_id_timestamp)
        if reference.startswith("chatpulse_"):
            parts = reference.split("_")
            if len(parts) >= 2:
                user_id = int(parts[1])
            else:
                return
        else:
            return
        
        # Find user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        
        # Determine plan based on amount
        plan = determine_plan_from_amount(amount)
        
        # Create or update subscription
        existing_subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()
        
        if existing_subscription:
            # Update existing subscription
            existing_subscription.status = "expired"
            db.commit()
        
        # Create new subscription
        new_subscription = Subscription(
            user_id=user_id,
            plan=plan,
            amount=amount,
            currency=currency,
            status="active",
            flutterwave_reference=reference,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        db.add(new_subscription)
        
        # Update user's subscription plan
        user.subscription_plan = plan
        user.subscription_status = "active"
        
        db.commit()
        
        print(f"Subscription updated for user {user_id}: {plan.value}")
        
    except Exception as e:
        print(f"Error handling successful payment: {e}")
        db.rollback()

async def handle_failed_payment(payment_data: dict, db: Session):
    """Handle failed payment."""
    
    try:
        reference = payment_data.get("tx_ref", "")
        
        if reference.startswith("chatpulse_"):
            parts = reference.split("_")
            if len(parts) >= 2:
                user_id = int(parts[1])
                
                # Log failed payment
                print(f"Payment failed for user {user_id}: {reference}")
        
    except Exception as e:
        print(f"Error handling failed payment: {e}")

def determine_plan_from_amount(amount: float) -> SubscriptionPlan:
    """Determine subscription plan from payment amount."""
    
    if amount >= 299.99:
        return SubscriptionPlan.ENTERPRISE
    elif amount >= 99.99:
        return SubscriptionPlan.PRO
    elif amount >= 29.99:
        return SubscriptionPlan.BASIC
    else:
        return SubscriptionPlan.FREE

@router.get("/test")
async def test_webhook():
    """Test webhook endpoint."""
    return {"status": "webhook endpoint is working"}
