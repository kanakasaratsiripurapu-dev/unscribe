"""Unsubscribe action model"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class UnsubscribeAction(Base):
    __tablename__ = "unsubscribe_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Action details
    action_type = Column(String(50), nullable=False)  # automated, manual_link, manual_phone, email_required
    status = Column(String(50), default='pending', index=True)  # pending, in_progress, awaiting_confirmation, confirmed, failed
    
    # Execution details
    unsubscribe_url = Column(String)
    http_method = Column(String(10))  # GET, POST
    form_data = Column(JSON)
    
    # Response tracking
    http_status_code = Column(Integer)
    response_body_snippet = Column(String)
    
    # Confirmation monitoring
    confirmation_email_id = Column(String(255))
    confirmation_detected_at = Column(DateTime)
    
    # Retry logic
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    # Error handling
    error_message = Column(String)
    requires_manual_action = Column(Boolean, default=False)
    manual_instructions = Column(String)
    
    # Timestamps
    initiated_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    monitoring_until = Column(DateTime, index=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="unsubscribe_actions")
    user = relationship("User")

