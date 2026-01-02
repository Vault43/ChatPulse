from fastapi import APIRouter, HTTPException, status, Request, Depends
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

# NOWPayments IPN secret
NOWPAYMENTS_IPN_SECRET = os.getenv("NOWPAYMENTS_IPN_SECRET")

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


@router.post("/nowpayments")
async def nowpayments_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """Handle NOWPayments IPN webhooks."""

    if not NOWPAYMENTS_IPN_SECRET:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NOWPayments webhook not configured"
        )

    body = await request.body()
    signature = request.headers.get("x-nowpayments-sig")
    if not signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing signature"
        )

    expected = hmac.new(
        NOWPAYMENTS_IPN_SECRET.encode(),
        body,
        hashlib.sha512
    ).hexdigest()

    if signature != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature"
        )

    try:
        payload = json.loads(body.decode())
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid JSON"
        )

    await handle_nowpayments_ipn(payload, db)
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


async def handle_nowpayments_ipn(ipn_data: dict, db: Session):
    """Activate subscription when NOWPayments payment is confirmed."""

    try:
        order_id = ipn_data.get("order_id") or ""
        payment_status = (ipn_data.get("payment_status") or "").lower()
        invoice_id = ipn_data.get("invoice_id")
        payment_id = ipn_data.get("payment_id")
        price_amount = float(ipn_data.get("price_amount", 0) or 0)
        price_currency = ipn_data.get("price_currency") or "USD"

        # We only activate on successful statuses
        if payment_status not in ("finished", "confirmed", "paid"):
            return

        # order_id is generated as: chatpulse_{user_id}_{plan_id}_{timestamp}
        if not order_id.startswith("chatpulse_"):
            return

        parts = order_id.split("_")
        if len(parts) < 4:
            return

        user_id = int(parts[1])
        plan_id = parts[2]

        plan_map = {
            "free": SubscriptionPlan.FREE,
            "basic": SubscriptionPlan.BASIC,
            "pro": SubscriptionPlan.PRO,
            "enterprise": SubscriptionPlan.ENTERPRISE,
        }
        plan = plan_map.get(plan_id)
        if not plan:
            return

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return

        # Expire existing active subscription
        existing_subscription = db.query(Subscription).filter(
            Subscription.user_id == user_id,
            Subscription.status == "active"
        ).first()

        if existing_subscription:
            existing_subscription.status = "expired"
            db.commit()

        reference = None
        if invoice_id:
            reference = f"nowpayments_invoice_{invoice_id}"
        elif payment_id:
            reference = f"nowpayments_payment_{payment_id}"
        else:
            reference = f"nowpayments_{order_id}"

        new_subscription = Subscription(
            user_id=user_id,
            plan=plan,
            amount=price_amount if price_amount > 0 else 0,
            currency=price_currency,
            status="active",
            payment_provider="nowpayments",
            nowpayments_reference=reference,
            started_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=30)
        )

        db.add(new_subscription)

        user.subscription_plan = plan
        user.subscription_status = "active"

        db.commit()
        print(f"NOWPayments subscription updated for user {user_id}: {plan.value}")

    except Exception as e:
        print(f"Error handling NOWPayments IPN: {e}")
        db.rollback()

@router.get("/test")
async def test_webhook():
    """Test webhook endpoint."""
    return {"status": "webhook endpoint is working"}
