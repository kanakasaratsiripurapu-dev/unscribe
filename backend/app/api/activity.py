"""Activity log endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models import ActivityLog
from typing import List
import uuid

router = APIRouter()


@router.get("/{user_id}")
async def get_activity_log(user_id: str, limit: int = 50, db: AsyncSession = Depends(get_db)) -> List[dict]:
    """Get activity log for a user"""
    try:
        result = await db.execute(
            select(ActivityLog)
            .where(ActivityLog.user_id == uuid.UUID(user_id))
            .order_by(desc(ActivityLog.created_at))
            .limit(limit)
        )
        activities = result.scalars().all()
        
        return [
            {
                "id": str(activity.id),
                "activity_type": activity.activity_type,
                "activity_description": activity.activity_description,
                "created_at": activity.created_at.isoformat()
            }
            for activity in activities
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get activity log: {str(e)}")

