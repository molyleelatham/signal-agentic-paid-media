"""
Campaign models.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class GoalType(str, Enum):
    """Campaign goal types."""
    LEAD_GENERATION = "lead_generation"
    CUSTOMER_ACQUISITION = "customer_acquisition"
    BRAND_AWARENESS = "brand_awareness"
    RETARGETING = "retargeting"


class CampaignStatus(str, Enum):
    """Campaign status types."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """Campaign model."""
    
    __tablename__ = "campaigns"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    goal_type: Mapped[str] = mapped_column(String(50), nullable=False)
    total_budget: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=CampaignStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Campaign(id={self.id}, name={self.name}, goal_type={self.goal_type}, status={self.status})>"