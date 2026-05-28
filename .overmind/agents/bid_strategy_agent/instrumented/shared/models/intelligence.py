"""
Intelligence and monitoring models.
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, JSON, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class IntelligenceDocument(Base):
    """Intelligence documents from Tavily and other sources."""
    
    __tablename__ = "intelligence_documents"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"))
    source_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # competitor, market, social, brand
    content: Mapped[str] = mapped_column(String, nullable=False)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    embedding: Mapped[Optional[bytes]] = mapped_column(LargeBinary)  # Vector embedding
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<IntelligenceDocument(source={self.source_type}, campaign_id={self.campaign_id})>"


class AdstockDecay(Base):
    """Adstock decay monitoring records."""
    
    __tablename__ = "adstock_decay"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    position_id: Mapped[str] = mapped_column(String(36), ForeignKey("media_positions.id"), nullable=False, index=True)
    lambda_decay: Mapped[Optional[float]] = mapped_column(String(50))  # Stored as string to avoid precision issues
    std_error: Mapped[Optional[float]] = mapped_column(String(50))
    signal: Mapped[str] = mapped_column(String(50), nullable=False)  # hold, reduce, exit
    confidence: Mapped[str] = mapped_column(String(50))
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<AdstockDecay(position_id={self.position_id}, signal={self.signal})>"