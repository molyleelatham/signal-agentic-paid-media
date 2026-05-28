"""
User models.
"""
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DECIMAL, String
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class User(Base):
    """User model."""
    
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    token_balance: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), default=Decimal("0.0"))
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, token_balance={self.token_balance})>"