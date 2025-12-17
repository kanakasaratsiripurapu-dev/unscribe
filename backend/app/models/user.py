"""User model"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255))
    gmail_refresh_token = Column(String, nullable=False)  # Encrypted
    gmail_token_encrypted_at = Column(DateTime)
    profile_picture_url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime)
    last_scan_at = Column(DateTime)
    subscription_count = Column(Integer, default=0)
    total_monthly_spend = Column(Numeric(10, 2), default=0.00)
    is_active = Column(Boolean, default=True, index=True)
    deleted_at = Column(DateTime, nullable=True)  # Soft delete
    
    # Relationships
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")

