"""Subscription management endpoints"""
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Subscription, User
from typing import List
import uuid

router = APIRouter()


@router.get("/")
async def list_subscriptions(user_id: str, db: AsyncSession = Depends(get_db)) -> List[dict]:
    """List all subscriptions for a user"""
    try:
        result = await db.execute(
            select(Subscription).where(
                Subscription.user_id == uuid.UUID(user_id),
                Subscription.status == 'active'
            )
        )
        subscriptions = result.scalars().all()
        
        return [
            {
                "id": str(sub.id),
                "service_name": sub.service_name,
                "price": float(sub.price),
                "currency": sub.currency,
                "billing_period": sub.billing_period,
                "next_renewal_date": sub.next_renewal_date.isoformat() if sub.next_renewal_date else None,
                "status": sub.status,
                "unsubscribe_link": sub.unsubscribe_link
            }
            for sub in subscriptions
        ]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list subscriptions: {str(e)}")


@router.post("/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Initiate cancellation for a subscription"""
    try:
        result = await db.execute(
            select(Subscription).where(
                Subscription.id == uuid.UUID(subscription_id),
                Subscription.user_id == uuid.UUID(user_id)
            )
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        # In production, queue Celery task for cancellation
        # from worker.tasks import execute_unsubscribe
        # execute_unsubscribe.delay(...)
        
        subscription.status = 'pending_cancellation'
        await db.commit()
        
        return {
            "subscription_id": str(subscription.id),
            "status": subscription.status,
            "message": "Cancellation initiated"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel subscription: {str(e)}")

