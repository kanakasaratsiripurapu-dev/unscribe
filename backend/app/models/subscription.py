"""Subscription model"""
from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Core subscription data
    service_name = Column(String(255), nullable=False, index=True)
    service_domain = Column(String(255))
    service_logo_url = Column(String)
    service_category = Column(String(100))
    
    # Pricing
    price = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default='USD')
    billing_period = Column(String(50), nullable=False)  # monthly, annually, quarterly, one-time
    
    # Dates
    first_detected_date = Column(Date)
    next_renewal_date = Column(Date, index=True)
    last_verified_date = Column(DateTime)
    
    # Links & metadata
    unsubscribe_link = Column(String)
    manage_account_link = Column(String)
    payment_method_last4 = Column(String(4))
    subscription_tier = Column(String(100))
    
    # Status
    status = Column(String(50), default='active', index=True)  # active, cancelled, pending_cancellation, expired
    
    # Detection metadata
    source_email_ids = Column(ARRAY(String))
    detection_confidence = Column(Numeric(3, 2))
    detected_by = Column(String(50))  # 'rule_based', 'llm', 'manual'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cancelled_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    events = relationship("SubscriptionEvent", back_populates="subscription", cascade="all, delete-orphan")
    unsubscribe_actions = relationship("UnsubscribeAction", back_populates="subscription", cascade="all, delete-orphan")

