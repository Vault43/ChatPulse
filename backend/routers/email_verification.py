from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from database import get_db, User
from utils.security import get_password_hash

router = APIRouter()

class EmailVerificationRequest(BaseModel):
    email: EmailStr

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str

class SignupWithVerificationRequest(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str = None
    company: str = None
    verification_code: str

# Store verification codes (in production, use Redis or database)
verification_codes = {}

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return secrets.randbelow(1000000)

def send_verification_email(email: str, code: str):
    """Send verification email with code"""
    try:
        # Email configuration (use environment variables in production)
        smtp_server = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        
        if not smtp_user or not smtp_password:
            # For development, just print the code
            print(f"📧 Verification code for {email}: {code}")
            return True
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email
        msg['Subject'] = 'ChatPulse - Email Verification Code'
        
        body = f"""
        <html>
        <body>
            <h2>Welcome to ChatPulse! 🎉</h2>
            <p>Your email verification code is:</p>
            <h3 style="background-color: #f0f0f0; padding: 10px; text-align: center; font-size: 24px; font-weight: bold;">
                {code}
            </h3>
            <p>This code will expire in 10 minutes.</p>
            <p>If you didn't request this code, please ignore this email.</p>
            <br>
            <p>Best regards,<br>The ChatPulse Team</p>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_user, email, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

@router.post("/send-verification")
async def send_verification_code(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    """Send verification code to email"""
    email = request.email
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate and store verification code
    code = f"{generate_verification_code():06d}"
    expiry_time = datetime.utcnow() + timedelta(minutes=10)
    
    verification_codes[email] = {
        "code": code,
        "expiry": expiry_time
    }
    
    # Send email
    email_sent = send_verification_email(email, code)
    
    return {
        "message": "Verification code sent successfully",
        "email_sent": email_sent,
        "expires_in_minutes": 10
    }

@router.post("/verify-code")
async def verify_code(request: VerifyCodeRequest):
    """Verify email verification code"""
    email = request.email
    code = request.code
    
    # Check if code exists and is valid
    if email not in verification_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code sent to this email"
        )
    
    stored_data = verification_codes[email]
    
    # Check if code has expired
    if datetime.utcnow() > stored_data["expiry"]:
        del verification_codes[email]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired"
        )
    
    # Check if code matches
    if stored_data["code"] != code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    return {
        "message": "Email verified successfully",
        "verified": True
    }

@router.post("/signup-with-verification")
async def signup_with_verification(request: SignupWithVerificationRequest, db: Session = Depends(get_db)):
    """Complete signup with verified email"""
    email = request.email
    username = request.username
    password = request.password
    full_name = request.full_name
    company = request.company
    verification_code = request.verification_code
    
    # Verify the code again
    if email not in verification_codes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No verification code sent to this email"
        )
    
    stored_data = verification_codes[email]
    
    if datetime.utcnow() > stored_data["expiry"]:
        del verification_codes[email]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired"
        )
    
    if stored_data["code"] != verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first()
    
    if existing_user:
        if existing_user.email == email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create user
    hashed_password = get_password_hash(password)
    user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        full_name=full_name,
        company=company,
        is_verified=True,  # Email is verified
        status='active',
        subscription_plan='free',
        created_at=datetime.utcnow()
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Clean up verification code
    del verification_codes[email]
    
    return {
        "message": "Account created successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "is_verified": user.is_verified
        }
    }
