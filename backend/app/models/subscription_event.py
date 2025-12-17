"""Subscription event model"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class SubscriptionEvent(Base):
    __tablename__ = "subscription_events"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    event_type = Column(String(100), nullable=False, index=True)  # detected, updated, renewal_reminder, price_change, cancelled
    event_description = Column(String)
    event_metadata = Column(JSON)
    triggered_by = Column(String(100))  # 'system', 'user', 'agent_name'
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    subscription = relationship("Subscription", back_populates="events")
    user = relationship("User")

