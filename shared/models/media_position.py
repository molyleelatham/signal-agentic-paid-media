"""
Media position models.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class PlatformType(str):
    """Platform types."""
    META = "meta"
    GOOGLE = "google"
    THRAD = "thrad"


class PositionStatus(str):
    """Position status types."""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class MediaPosition(Base):
    """Media position (ad) model."""
    
    __tablename__ = "media_positions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    topic_cluster_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("topic_clusters.id"))
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    creative_id: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default=PositionStatus.ACTIVE)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<MediaPosition(id={self.id}, platform={self.platform}, status={self.status})>"