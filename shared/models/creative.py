"""
Creative asset models.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import String, ForeignKey, JSON, DECIMAL, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class Creative(Base):
    """Creative assets for advertising campaigns."""
    
    __tablename__ = "creatives"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"))
    
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Creative details
    creative_type: Mapped[str] = mapped_column(String(50), nullable=False)  # video, image, carousel, static
    format: Mapped[str] = mapped_column(String(50))  # vertical, horizontal, square
    platform: Mapped[Optional[str]] = mapped_column(String(50))  # meta, google, tiktok, etc.
    
    # Asset URLs
    asset_url: Mapped[Optional[str]] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Creative content
    headline: Mapped[Optional[str]] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String(500))
    cta_text: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Metadata
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, review, approved, active, paused
    
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Creative(id={self.id}, name={self.name}, type={self.creative_type}, status={self.status})>"


class CreativePlacement(Base):
    """Creative placement configurations across platforms."""
    
    __tablename__ = "creative_placements"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    creative_id: Mapped[str] = mapped_column(String(36), ForeignKey("creatives.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # meta, google, tiktok, microsoft
    placement_type: Mapped[str] = mapped_column(String(100))  # feed, story, in_feed, top_view, etc.
    
    # Platform-specific IDs
    platform_creative_id: Mapped[Optional[str]] = mapped_column(String(255))
    platform_placement_id: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Placement settings
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    start_date: Mapped[Optional[datetime]] = mapped_column(String(50))
    end_date: Mapped[Optional[datetime]] = mapped_column(String(50))
    
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<CreativePlacement(creative_id={self.creative_id}, platform={self.platform}, placement={self.placement_type})>"