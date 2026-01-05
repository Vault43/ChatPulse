from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
import os
import secrets
from datetime import datetime, timedelta

from database import get_db, User
from utils.security import create_access_token, verify_token

router = APIRouter()

# Google OAuth configuration
config = Config(environ=os.environ.copy())
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

class GoogleAuthResponse(BaseModel):
    access_token: str
    user: dict
    is_new_user: bool

@router.get('/google')
async def google_login(request: Request):
    """Initiate Google OAuth login."""
    redirect_uri = f"{os.getenv('FRONTEND_URL', 'https://precious-torte-91796f.netlify.app')}/auth/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get('/google/callback', response_model=GoogleAuthResponse)
async def google_auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    try:
        # Get the token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve user information from Google"
            )
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required from Google"
            )
        
        # Check if user exists
        user = db.query(User).filter(User.email == email).first()
        is_new_user = False
        
        if not user:
            # Create new user
            is_new_user = True
            user = User(
                username=email.split('@')[0],  # Use email prefix as username
                email=email,
                full_name=name,
                google_id=google_id,
                avatar_url=picture,
                is_verified=True,  # Google users are pre-verified
                status='active',
                subscription_plan='free',
                created_at=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user with Google info if not already set
            if not user.google_id:
                user.google_id = google_id
            if not user.avatar_url and picture:
                user.avatar_url = picture
            if not user.is_verified:
                user.is_verified = True
            user.last_login = datetime.utcnow()
            db.commit()
        
        # Create JWT token
        access_token = create_access_token(data={"sub": user.email})
        
        return GoogleAuthResponse(
            access_token=access_token,
            user={
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "avatar_url": user.avatar_url,
                "subscription_plan": user.subscription_plan,
                "is_verified": user.is_verified
            },
            is_new_user=is_new_user
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )

@router.post('/google/link')
async def link_google_account(
    request: Request,
    credentials: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Link Google account to existing user."""
    try:
        # Get the token from Google
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not retrieve user information from Google"
            )
        
        google_id = user_info.get('sub')
        email = user_info.get('email')
        picture = user_info.get('picture')
        
        # Get current user from JWT
        current_email = credentials.get("sub")
        user = db.query(User).filter(User.email == current_email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check if Google account is already linked to another user
        existing_google_user = db.query(User).filter(User.google_id == google_id).first()
        if existing_google_user and existing_google_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Google account is already linked to another user"
            )
        
        # Link Google account
        user.google_id = google_id
        if picture:
            user.avatar_url = picture
        user.is_verified = True
        db.commit()
        
        return {"message": "Google account linked successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to link Google account: {str(e)}"
        )

@router.post('/google/unlink')
async def unlink_google_account(
    credentials: dict = Depends(verify_token),
    db: Session = Depends(get_db)
):
    """Unlink Google account from user."""
    email = credentials.get("sub")
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Google account linked"
        )
    
    # Check if user has password
    if not user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlink Google account without setting a password first"
        )
    
    user.google_id = None
    db.commit()
    
    return {"message": "Google account unlinked successfully"}
