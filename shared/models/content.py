"""
Content and creative brief models.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, JSON, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class ContentBrief(Base):
    """Content briefs generated from intelligence analysis."""
    
    __tablename__ = "content_briefs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    topic_cluster_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("topic_clusters.id"))
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Brief content
    strategic_angle: Mapped[Optional[str]] = mapped_column(String(500))
    hook_type: Mapped[Optional[str]] = mapped_column(String(100))
    proof_point: Mapped[Optional[str]] = mapped_column(String(500))
    cta: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Targeting
    target_audience: Mapped[Optional[str]] = mapped_column(String(255))
    platform: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, approved, in_production, completed
    priority: Mapped[str] = mapped_column(String(20), default="medium")  # low, medium, high
    
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ContentBrief(id={self.id}, name={self.name}, status={self.status})>"