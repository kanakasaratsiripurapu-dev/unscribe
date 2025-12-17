"""Email scanning endpoints"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User, EmailImportSession
from app.services.gmail_service import gmail_service
from app.utils.encryption import decrypt_token
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/start")
async def start_scan(
    user_id: str,
    date_range_years: int = 3,
    db: AsyncSession = Depends(get_db)
):
    """Start email scanning process"""
    try:
        # Get user
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Create scan session
        session = EmailImportSession(
            user_id=user.id,
            status='running',
            scan_params={"date_range_years": date_range_years}
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # In production, queue Celery task here
        # from worker.tasks import scan_gmail_inbox
        # scan_gmail_inbox.delay(str(user.id), str(session.id), date_range_years)
        
        return {
            "session_id": str(session.id),
            "status": session.status,
            "started_at": session.started_at.isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start scan: {str(e)}")


@router.get("/status/{session_id}")
async def get_scan_status(session_id: str, db: AsyncSession = Depends(get_db)):
    """Get scan progress status"""
    try:
        result = await db.execute(
            select(EmailImportSession).where(EmailImportSession.id == uuid.UUID(session_id))
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": str(session.id),
            "status": session.status,
            "total_emails_found": session.total_emails_found,
            "emails_processed": session.emails_processed,
            "subscriptions_found": session.subscriptions_found,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

