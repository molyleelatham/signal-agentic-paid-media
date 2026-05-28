"""
Trading-related models.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class BidDecision(Base):
    """Bid decision records."""
    
    __tablename__ = "bid_decisions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    position_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("media_positions.id"))
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    bid_amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    intent_context: Mapped[Optional[dict]] = mapped_column(JSON)
    loess_optimal: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    posterior_confidence: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 4))
    decay_signal: Mapped[Optional[str]] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # bid, pause, skip
    reason: Mapped[Optional[str]] = mapped_column(String(255))
    agent_decision: Mapped[Optional[bool]] = mapped_column(Integer, default=False)  # True if made by AI agent
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<BidDecision(platform={self.platform}, bid={self.bid_amount}, action={self.action})>"


class BudgetAllocation(Base):
    """Budget allocation records (Thompson sampling)."""
    
    __tablename__ = "trading_budget_allocations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    allocated_budget: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    alpha: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), default=Decimal("2.0"))
    beta: Mapped[Decimal] = mapped_column(DECIMAL(10, 4), default=Decimal("2.0"))
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<BudgetAllocation(campaign_id={self.campaign_id}, platform={self.platform}, budget={self.allocated_budget})>"