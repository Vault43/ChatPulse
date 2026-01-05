from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from database import engine, Base, SessionLocal
from routers import auth, users, chat, ai, subscriptions, webhooks, google_auth, email_verification
from utils.security import verify_token

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Run migrations for Google OAuth fields
    db = SessionLocal()
    try:
        # Check if google_id column exists
        result = db.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users' AND column_name = 'google_id'")
        if not result.fetchone():
            print("Adding Google OAuth fields to users table...")
            db.execute("ALTER TABLE users ADD COLUMN google_id VARCHAR(255) UNIQUE")
            db.execute("ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500)")
            db.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
            db.execute("ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL")
            db.commit()
            print("✅ Google OAuth fields added successfully")
        else:
            print("✅ Google OAuth fields already exist")
    except Exception as e:
        print(f"Migration error: {e}")
        db.rollback()
    finally:
        db.close()
    
    yield
    # Shutdown
    pass

app = FastAPI(
    title="ChatPulse API",
    description="AI Auto-reply SaaS Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://precious-torte-91796f.netlify.app",
        "http://localhost:3000",
        "*"  # Fallback for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(email_verification.router, prefix="/api/auth", tags=["email-verification"])
app.include_router(google_auth.router, prefix="/api/auth/google", tags=["google-auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["subscriptions"])
app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/")
async def root():
    return {"message": "ChatPulse API - AI Auto-reply Platform", "version": "1.0.0"}

@app.options("/{path:path}")
async def options_handler(path: str):
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ChatPulse API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
