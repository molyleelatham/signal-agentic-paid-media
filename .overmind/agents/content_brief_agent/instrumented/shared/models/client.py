"""
Client and account models.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, String, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class Client(Base):
    """Client model for businesses using the platform."""
    
    __tablename__ = "clients"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, inactive, trial
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Client(id={self.id}, name={self.name}, industry={self.industry})>"


class ClientGoal(Base):
    """Client goals and targets."""
    
    __tablename__ = "client_goals"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    goal_type: Mapped[str] = mapped_column(String(50), nullable=False)  # lead_generation, customer_acquisition, revenue_growth
    target_value: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    current_value: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), default=Decimal("0.0"))
    period: Mapped[str] = mapped_column(String(50), default="weekly")  # weekly, monthly, quarterly
    start_date: Mapped[Optional[datetime]] = mapped_column(String(50))
    end_date: Mapped[Optional[datetime]] = mapped_column(String(50))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ClientGoal(client_id={self.client_id}, goal_type={self.goal_type}, target={self.target_value})>"


class ClientPlatform(Base):
    """Platform configurations for clients."""
    
    __tablename__ = "client_platforms"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # meta, google, tiktok, microsoft
    account_id: Mapped[Optional[str]] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    configuration: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ClientPlatform(client_id={self.client_id}, platform={self.platform})>"