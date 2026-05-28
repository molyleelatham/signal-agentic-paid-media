"""
Token economy models.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class TransactionType(str):
    """Token transaction types."""
    REWARD = "reward"
    PENALTY = "penalty"
    STAKE = "stake"
    UNSTAKE = "unstake"
    TRANSFER = "transfer"


class TokenTransaction(Base):
    """Token transaction model."""
    
    __tablename__ = "token_transactions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    position_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("media_positions.id"))
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<TokenTransaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"


class StakeStatus(str):
    """Stake status types."""
    ACTIVE = "active"
    COMPLETED = "completed"
    LIQUIDATED = "liquidated"


class TokenStake(Base):
    """Token stake model."""
    
    __tablename__ = "token_stakes"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False)
    strategy_id: Mapped[Optional[str]] = mapped_column(String(255))
    stake_amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    multiplier: Mapped[Decimal] = mapped_column(DECIMAL(5, 4), default=Decimal("1.0"))
    status: Mapped[str] = mapped_column(String(50), default=StakeStatus.ACTIVE)
    staked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    unstaked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<TokenStake(id={self.id}, amount={self.stake_amount}, multiplier={self.multiplier}, status={self.status})>"