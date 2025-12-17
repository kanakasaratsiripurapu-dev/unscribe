"""Authentication endpoints"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.services.gmail_service import gmail_service
from app.utils.encryption import encrypt_token
from datetime import datetime
import uuid

router = APIRouter()


@router.get("/login")
async def initiate_login():
    """Initiate Google OAuth flow"""
    try:
        auth_url, state = gmail_service.create_oauth_flow()
        return {"auth_url": auth_url, "state": state}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate login: {str(e)}")


@router.post("/callback")
async def oauth_callback(
    code: str = Query(..., description="OAuth authorization code"),
    state: str = Query(..., description="OAuth state parameter"),
    db: AsyncSession = Depends(get_db)
):
    """Handle OAuth callback and create/update user"""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"OAuth callback received - Code length: {len(code) if code else 0}, State: {state[:20] if state else 'None'}...")
        # Exchange code for tokens
        tokens = await gmail_service.exchange_code_for_tokens(code, state)
        
        user_info = tokens["user_info"]
        email = user_info["email"]
        
        # Check if user exists
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        
        # Encrypt refresh token
        encrypted_token = encrypt_token(tokens["refresh_token"])
        
        if user:
            # Update existing user
            user.gmail_refresh_token = encrypted_token
            user.gmail_token_encrypted_at = datetime.utcnow()
            user.last_login_at = datetime.utcnow()
            user.profile_picture_url = user_info.get("picture")
        else:
            # Create new user
            user = User(
                email=email,
                full_name=user_info.get("name"),
                gmail_refresh_token=encrypted_token,
                gmail_token_encrypted_at=datetime.utcnow(),
                profile_picture_url=user_info.get("picture"),
                last_login_at=datetime.utcnow()
            )
            db.add(user)
        
        await db.commit()
        await db.refresh(user)
        
        return {
            "user_id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "access_token": tokens["access_token"]  # In production, use JWT
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")

