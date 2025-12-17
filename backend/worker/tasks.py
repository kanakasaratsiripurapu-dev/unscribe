"""
Celery background tasks for email scanning and subscription detection
"""
from celery import Celery, Task
from typing import Dict
import logging
from datetime import datetime, timedelta

from app.config import settings
from app.services.gmail_service import gmail_service
from app.services.detection_service import detection_service
from app.services.unsubscribe_service import unsubscribe_service
from app.database import AsyncSessionLocal
from app.models import User, Subscription, EmailImportSession, UnsubscribeAction
from app.utils.encryption import decrypt_token
from sqlalchemy import select

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'subscout_worker',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
)


@celery_app.task(bind=True, name='scan_gmail_inbox')
def scan_gmail_inbox(self: Task, user_id: str, session_id: str, date_range_years: int = 3):
    """
    Main task: Scan user's Gmail inbox for subscriptions
    """
    logger.info(f"Starting Gmail scan for user {user_id}, session {session_id}")
    
    import asyncio
    return asyncio.run(_scan_gmail_inbox_async(self, user_id, session_id, date_range_years))


async def _scan_gmail_inbox_async(task: Task, user_id: str, session_id: str, date_range_years: int):
    """Async implementation of scan task"""
    
    async with AsyncSessionLocal() as db:
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            logger.error(f"User {user_id} not found")
            return {"error": "User not found"}
        
        # Get session
        result = await db.execute(
            select(EmailImportSession).where(EmailImportSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return {"error": "Session not found"}
        
        try:
            # Refresh access token (decrypt refresh token first)
            decrypted_token = decrypt_token(user.gmail_refresh_token)
            access_token = await gmail_service.refresh_access_token(decrypted_token)
            
            # Build Gmail search query
            date_filter = (datetime.now() - timedelta(days=365 * date_range_years)).strftime('%Y/%m/%d')
            query = f"{settings.EMAIL_SEARCH_QUERY} after:{date_filter}"
            
            # Fetch email list (paginated)
            total_processed = 0
            total_subscriptions_found = 0
            page_token = None
            
            while True:
                # Fetch batch of email IDs
                result_dict = await gmail_service.fetch_emails(
                    access_token=access_token,
                    query=query,
                    max_results=settings.GMAIL_BATCH_SIZE,
                    page_token=page_token
                )
                
                message_list = result_dict.get('messages', [])
                if not message_list:
                    break
                
                # Update session with total count (first batch only)
                if page_token is None:
                    session.total_emails_found = result_dict.get('resultSizeEstimate', 0)
                    await db.commit()
                
                # Fetch and process emails in this batch
                message_ids = [msg['id'] for msg in message_list]
                
                async for email_data in gmail_service.batch_fetch_emails(
                    access_token=access_token,
                    message_ids=message_ids
                ):
                    total_processed += 1
                    
                    # Detect subscription
                    subscription_data = await detection_service.detect_subscription(email_data)
                    
                    if subscription_data:
                        # Save subscription to database
                        await _save_subscription(db, user_id, subscription_data)
                        total_subscriptions_found += 1
                        
                        logger.info(
                            f"Found subscription: {subscription_data['service_name']} "
                            f"(${subscription_data['price']}/{subscription_data['billing_period']})"
                        )
                    
                    # Update progress every 100 emails
                    if total_processed % 100 == 0:
                        session.emails_processed = total_processed
                        session.subscriptions_found = total_subscriptions_found
                        await db.commit()
                        
                        # Update Celery task state for real-time progress
                        task.update_state(
                            state='PROGRESS',
                            meta={
                                'processed': total_processed,
                                'total': session.total_emails_found,
                                'subscriptions_found': total_subscriptions_found
                            }
                        )
                
                # Check if there are more pages
                page_token = result_dict.get('nextPageToken')
                if not page_token:
                    break
            
            # Mark session as completed
            session.status = 'completed'
            session.emails_processed = total_processed
            session.subscriptions_found = total_subscriptions_found
            session.completed_at = datetime.utcnow()
            
            # Update user stats
            user.last_scan_at = datetime.utcnow()
            user.subscription_count = total_subscriptions_found
            
            await db.commit()
            
            logger.info(
                f"Scan completed: {total_processed} emails processed, "
                f"{total_subscriptions_found} subscriptions found"
            )
            
            return {
                "status": "completed",
                "emails_processed": total_processed,
                "subscriptions_found": total_subscriptions_found
            }
        
        except Exception as e:
            logger.error(f"Error during scan: {e}", exc_info=True)
            
            # Mark session as failed
            session.status = 'failed'
            session.error_message = str(e)
            await db.commit()
            
            return {"error": str(e)}


async def _save_subscription(db, user_id: str, subscription_data: Dict):
    """
    Save detected subscription to database
    Handles deduplication
    """
    from sqlalchemy.dialects.postgresql import insert
    
    # Check if subscription already exists (same service + user)
    result = await db.execute(
        select(Subscription).where(
            Subscription.user_id == user_id,
            Subscription.service_name == subscription_data['service_name'],
            Subscription.status == 'active'
        )
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        # Update existing subscription with newer data
        existing.price = subscription_data.get('price', existing.price)
        existing.currency = subscription_data.get('currency', existing.currency)
        existing.billing_period = subscription_data.get('billing_period', existing.billing_period)
        existing.next_renewal_date = subscription_data.get('next_renewal_date', existing.next_renewal_date)
        existing.unsubscribe_link = subscription_data.get('unsubscribe_link', existing.unsubscribe_link)
        existing.detection_confidence = subscription_data.get('confidence', existing.detection_confidence)
        existing.last_verified_date = datetime.utcnow()
        
        # Append new source email ID
        if subscription_data.get('source_email_id'):
            if existing.source_email_ids:
                existing.source_email_ids.append(subscription_data['source_email_id'])
            else:
                existing.source_email_ids = [subscription_data['source_email_id']]
        
        logger.info(f"Updated existing subscription: {existing.service_name}")
    
    else:
        # Create new subscription
        new_subscription = Subscription(
            user_id=user_id,
            service_name=subscription_data['service_name'],
            price=subscription_data['price'],
            currency=subscription_data.get('currency', 'USD'),
            billing_period=subscription_data['billing_period'],
            next_renewal_date=subscription_data.get('next_renewal_date'),
            unsubscribe_link=subscription_data.get('unsubscribe_link'),
            subscription_tier=subscription_data.get('subscription_tier'),
            detection_confidence=subscription_data.get('confidence', 0.5),
            detected_by=subscription_data.get('detected_by', 'llm'),
            source_email_ids=[subscription_data.get('source_email_id')],
            first_detected_date=datetime.utcnow().date(),
            last_verified_date=datetime.utcnow(),
            status='active'
        )
        
        db.add(new_subscription)
        logger.info(f"Created new subscription: {new_subscription.service_name}")
    
    await db.commit()


@celery_app.task(name='execute_unsubscribe')
def execute_unsubscribe(subscription_id: str, action_id: str, user_access_token: str):
    """
    Task: Execute unsubscribe action
    """
    import asyncio
    return asyncio.run(_execute_unsubscribe_async(subscription_id, action_id, user_access_token))


async def _execute_unsubscribe_async(subscription_id: str, action_id: str, user_access_token: str):
    """Async implementation of unsubscribe task"""
    
    async with AsyncSessionLocal() as db:
        # Get subscription
        result = await db.execute(
            select(Subscription).where(Subscription.id == subscription_id)
        )
        subscription = result.scalar_one_or_none()
        
        if not subscription:
            return {"error": "Subscription not found"}
        
        # Get unsubscribe action
        result = await db.execute(
            select(UnsubscribeAction).where(UnsubscribeAction.id == action_id)
        )
        action = result.scalar_one_or_none()
        
        if not action:
            return {"error": "Unsubscribe action not found"}
        
        try:
            # Update action status
            action.status = 'in_progress'
            await db.commit()
            
            # Attempt cancellation
            result = await unsubscribe_service.initiate_cancellation(
                subscription_id=subscription_id,
                unsubscribe_url=subscription.unsubscribe_link,
                user_access_token=user_access_token
            )
            
            # Update action with result
            action.action_type = result['action_type']
            action.http_status_code = result.get('http_status')
            action.requires_manual_action = result['requires_user_action']
            
            if result['requires_user_action']:
                action.manual_instructions = result.get('instructions', '')
            
            if result['status'] == 'success':
                action.status = 'awaiting_confirmation'
                action.monitoring_until = datetime.utcnow() + timedelta(
                    days=settings.CONFIRMATION_MONITORING_DAYS
                )
                subscription.status = 'pending_cancellation'
                
                # Schedule confirmation monitoring task
                celery_app.send_task(
                    'monitor_cancellation_confirmation',
                    args=[subscription_id, action_id, user_access_token],
                    countdown=3600  # Check in 1 hour
                )
            
            elif result['status'] == 'manual_required':
                action.status = 'manual_required'
            
            else:
                action.status = 'failed'
                action.error_message = result.get('message', 'Unknown error')
            
            await db.commit()
            
            return result
        
        except Exception as e:
            logger.error(f"Unsubscribe execution failed: {e}", exc_info=True)
            
            action.status = 'failed'
            action.error_message = str(e)
            await db.commit()
            
            return {"error": str(e)}


# Celery beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    'check_renewal_reminders': {
        'task': 'send_renewal_reminders',
        'schedule': 86400.0,  # Daily
    },
}

