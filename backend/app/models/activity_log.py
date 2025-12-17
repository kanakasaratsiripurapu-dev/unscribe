"""Activity log model"""
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class ActivityLog(Base):
    __tablename__ = "activity_log"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    activity_type = Column(String(100), nullable=False, index=True)  # scan_started, scan_completed, subscription_detected, etc.
    activity_description = Column(String, nullable=False)
    
    # Related entities
    related_subscription_id = Column(UUID(as_uuid=True))
    related_session_id = Column(UUID(as_uuid=True))
    related_action_id = Column(UUID(as_uuid=True))
    
    # Metadata
    activity_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")

