"""Email import session model"""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from app.database import Base


class EmailImportSession(Base):
    __tablename__ = "email_import_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(String(50), default='running', index=True)  # running, completed, failed, cancelled
    total_emails_found = Column(Integer, default=0)
    emails_processed = Column(Integer, default=0)
    subscriptions_found = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime)
    error_message = Column(String)
    scan_params = Column(JSON)  # Store search filters, date range, etc.
    
    # Relationships
    user = relationship("User")

