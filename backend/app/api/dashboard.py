"""Dashboard endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models import User, Subscription
import uuid

router = APIRouter()


@router.get("/stats/{user_id}")
async def get_dashboard_stats(user_id: str, db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics for a user"""
    try:
        # Get user
        result = await db.execute(select(User).where(User.id == uuid.UUID(user_id)))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get subscription stats
        result = await db.execute(
            select(
                func.count(Subscription.id),
                func.sum(
                    func.case(
                        (Subscription.billing_period == 'monthly', Subscription.price),
                        (Subscription.billing_period == 'annually', Subscription.price / 12),
                        (Subscription.billing_period == 'quarterly', Subscription.price / 3),
                        else_=0
                    )
                )
            ).where(
                Subscription.user_id == user.id,
                Subscription.status == 'active'
            )
        )
        
        count, monthly_spend = result.first()
        
        return {
            "total_subscriptions": count or 0,
            "estimated_monthly_spend": float(monthly_spend or 0),
            "estimated_annual_spend": float((monthly_spend or 0) * 12),
            "last_scan_at": user.last_scan_at.isoformat() if user.last_scan_at else None
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

