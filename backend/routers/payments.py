from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import json
import requests
from datetime import datetime, timedelta
from database import get_db, User, Subscription
from auth import get_current_user

router = APIRouter(prefix="/api/payments", tags=["payments"])

class PaymentRequest(BaseModel):
    plan_id: int
    payment_method: str
    card_number: Optional[str] = None
    expiry: Optional[str] = None
    cvv: Optional[str] = None
    cardholder_name: Optional[str] = None
    email: Optional[EmailStr] = None

class FlutterwavePaymentRequest(BaseModel):
    email: EmailStr
    amount: float
    currency: str = "USD"
    tx_ref: str

@router.post("/subscribe")
async def subscribe(
    payment_data: PaymentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Process subscription payment
    """
    try:
        # Get plan details
        # For now, use mock plan data
        plans = {
            1: {"name": "Starter", "price": 9.99, "duration_days": 30},
            2: {"name": "Professional", "price": 29.99, "duration_days": 30},
            3: {"name": "Enterprise", "price": 99.99, "duration_days": 30}
        }
        
        if payment_data.plan_id not in plans:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid plan selected"
            )
        
        plan = plans[payment_data.plan_id]
        
        if payment_data.payment_method == "flutterwave":
            # Process Flutterwave payment
            flutterwave_data = {
                "email": payment_data.email,
                "amount": plan["price"],
                "currency": "USD",
                "tx_ref": f"CP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
            
            # Get Flutterwave keys from environment
            flutterwave_public_key = os.getenv("FLUTTERWAVE_PUBLIC_KEY")
            flutterwave_secret_key = os.getenv("FLUTTERWAVE_SECRET_KEY")
            
            if not flutterwave_public_key or not flutterwave_secret_key:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Payment service not configured"
                )
            
            # Create Flutterwave payment link
            headers = {
                "Authorization": f"Bearer {flutterwave_secret_key}",
                "Content-Type": "application/json"
            }
            
            payment_payload = {
                "public_key": flutterwave_public_key,
                "tx_ref": flutterwave_data["tx_ref"],
                "amount": flutterwave_data["amount"],
                "currency": flutterwave_data["currency"],
                "customer_email": flutterwave_data["email"],
                "redirect_url": f"{os.getenv('FRONTEND_URL', 'http://localhost:3000')}/payment/success",
                "payment_options": "card,banktransfer,ussd"
            }
            
            response = requests.post(
                "https://api.flutterwave.com/v3/payments",
                json=payment_payload,
                headers=headers
            )
            
            if response.status_code == 200:
                payment_response = response.json()
                if payment_response.get("status") == "success":
                    # Create subscription record
                    subscription = Subscription(
                        user_id=current_user.id,
                        plan_id=payment_data.plan_id,
                        plan_name=plan["name"],
                        amount=plan["price"],
                        duration_days=plan["duration_days"],
                        status="pending",
                        payment_method="flutterwave",
                        payment_reference=flutterwave_data["tx_ref"],
                        flutterwave_transaction_id=payment_response.get("data", {}).get("id"),
                        created_at=datetime.utcnow()
                    )
                    db.add(subscription)
                    db.commit()
                    
                    return {
                        "payment_url": payment_response["data"]["link"],
                        "tx_ref": flutterwave_data["tx_ref"]
                    }
            
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create payment"
            )
        
        elif payment_data.payment_method == "card":
            # Process card payment (mock implementation)
            # In production, integrate with Stripe or other card processor
            subscription = Subscription(
                user_id=current_user.id,
                plan_id=payment_data.plan_id,
                plan_name=plan["name"],
                amount=plan["price"],
                duration_days=plan["duration_days"],
                status="active",
                payment_method="card",
                payment_reference=f"CARD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=plan["duration_days"])
            )
            db.add(subscription)
            db.commit()
            
            return {
                "status": "success",
                "message": "Payment processed successfully",
                "redirect_url": "/payment/success"
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid payment method"
            )
            
    except Exception as e:
        print(f"Payment error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Payment processing failed"
        )

@router.post("/flutterwave/webhook")
async def flutterwave_webhook(
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Handle Flutterwave webhook notifications
    """
    try:
        # Verify webhook signature (implementation needed)
        tx_ref = payload.get("txRef")
        status = payload.get("status")
        
        if status == "successful":
            # Update subscription status
            subscription = db.query(Subscription).filter(
                Subscription.payment_reference == tx_ref
            ).first()
            
            if subscription:
                subscription.status = "active"
                subscription.expires_at = datetime.utcnow() + timedelta(days=subscription.duration_days)
                db.commit()
        
        return {"status": "received"}
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return {"status": "error"}

@router.get("/plans")
async def get_subscription_plans():
    """
    Get available subscription plans
    """
    plans = [
        {
            "plan_id": 1,
            "name": "Starter",
            "price": 9.99,
            "duration_days": 30,
            "features": [
                "500 messages per month",
                "Basic AI responses", 
                "Email support",
                "1 user account"
            ],
            "popular": False
        },
        {
            "plan_id": 2,
            "name": "Professional",
            "price": 29.99,
            "duration_days": 30,
            "features": [
                "Unlimited messages",
                "Advanced AI responses",
                "Priority support",
                "5 user accounts",
                "Custom AI rules",
                "Analytics dashboard"
            ],
            "popular": True
        },
        {
            "plan_id": 3,
            "name": "Enterprise",
            "price": 99.99,
            "duration_days": 30,
            "features": [
                "Unlimited everything",
                "Custom AI training",
                "Dedicated support",
                "Unlimited users",
                "White-label option",
                "API access",
                "Custom integrations"
            ],
            "popular": False
        }
    ]
    
    return {"plans": plans}

@router.get("/status")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's subscription status
    """
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        return {
            "status": "free",
            "plan": None,
            "expires_at": None
        }
    
    return {
        "status": subscription.status,
        "plan": {
            "name": subscription.plan_name,
            "amount": subscription.amount,
            "duration_days": subscription.duration_days
        },
        "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None
    }

@router.post("/cancel")
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel user's subscription
    """
    subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.status == "active"
    ).first()
    
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active subscription found"
        )
    
    subscription.status = "cancelled"
    subscription.cancelled_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Subscription cancelled successfully"}
