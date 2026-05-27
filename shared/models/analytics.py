"""
Analytics and optimization models.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, Date, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class PnLScore(Base):
    """P&L score records."""
    
    __tablename__ = "pnl_scores"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    position_id: Mapped[str] = mapped_column(String(36), ForeignKey("media_positions.id"), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    gross_revenue: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    attention_waste_cost: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    net_pnl: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    efficiency_ratio: Mapped[Decimal] = mapped_column(DECIMAL(10, 4))
    lambda_applied: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), default=Decimal("2.0"))
    token_reward: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), default=Decimal("0.0"))
    token_penalty: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), default=Decimal("0.0"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<PnLScore(position_id={self.position_id}, net_pnl={self.net_pnl})>"


class OvermindTrace(Base):
    """Overmind trace records."""
    
    __tablename__ = "overmind_traces"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    trace_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    function_name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_data: Mapped[Optional[dict]] = mapped_column(JSON)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    cost_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 6))
    quality_score: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(5, 4))
    outcome_label: Mapped[Optional[str]] = mapped_column(String(50))
    outcome_value: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(18, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<OvermindTrace(trace_id={self.trace_id}, function={self.function_name})>"