from sqlalchemy import Column, String, UUID, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from app.db.base import Base
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenant.id"), nullable=False)
    title = Column(String(255), nullable=False)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("user.id"))
    status = Column(String(50), nullable=False, default=TaskStatus.PENDING)
    created_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    due_at = Column(DateTime(timezone=True))
    meta = Column(JSONB, default=dict)