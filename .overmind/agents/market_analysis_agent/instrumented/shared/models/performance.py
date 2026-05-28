"""
Performance data models.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, Date, ForeignKey, String, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class PerformanceData(Base):
    """Performance data for media positions."""
    
    __tablename__ = "performance_data"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    position_id: Mapped[str] = mapped_column(String(36), ForeignKey("media_positions.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    impressions: Mapped[int] = mapped_column(Integer, default=0)
    clicks: Mapped[int] = mapped_column(Integer, default=0)
    conversions: Mapped[int] = mapped_column(Integer, default=0)
    spend: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), default=Decimal("0.0"))
    revenue: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), default=Decimal("0.0"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<PerformanceData(position_id={self.position_id}, date={self.date}, conversions={self.conversions})>"