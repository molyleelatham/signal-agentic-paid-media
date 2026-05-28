"""
Topic cluster models from BERTopic.
"""
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class ZoneType(str, Enum):
    """Gap matrix zone types."""
    GAP = "gap"  # High demand, competitors present, brand absent
    CONTESTED = "contested"  # High demand, competitors present, brand present
    OWNED = "owned"  # High demand, competitors absent, brand present
    IGNORE = "ignore"  # Low demand
    MONITOR = "monitor"  # Ambiguous


class TopicCluster(Base):
    """Topic cluster model from BERTopic."""
    
    __tablename__ = "topic_clusters"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    zone: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    competitor_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 4))
    intent_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 4))
    brand_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 4))
    velocity: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 4))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<TopicCluster(id={self.id}, name={self.name}, zone={self.zone})>"