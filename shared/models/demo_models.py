"""
Additional database models for demo data.
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, Date, ForeignKey, String, JSON, Integer, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column

from shared.database import Base


class ModelPerformance(Base):
    """Track model predictions vs actual outcomes."""
    
    __tablename__ = "model_performance"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Prediction details
    prediction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # bid, budget, keyword, creative
    input_data: Mapped[Optional[dict]] = mapped_column(JSON)
    predicted_value: Mapped[Decimal] = mapped_column(DECIMAL(18, 4), nullable=False)
    actual_value: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(18, 4))
    
    # Accuracy metrics
    absolute_error: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(18, 4))
    percentage_error: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 4))
    is_accurate: Mapped[Optional[bool]] = mapped_column(Boolean)
    
    # Context
    client_id: Mapped[Optional[str]] = mapped_column(String(36))
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36))
    
    prediction_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    actual_date: Mapped[Optional[date]] = mapped_column(Date)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ModelPerformance(model={self.model_name}, pred={self.predicted_value}, actual={self.actual_value})>"


class KeywordPerformance(Base):
    """Track individual keyword performance metrics."""
    
    __tablename__ = "keyword_performance"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    match_type: Mapped[str] = mapped_column(String(20), nullable=False)  # broad, phrase, exact
    
    # Performance metrics
    impressions: Mapped[int] = mapped_column(Integer, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False)
    conversions: Mapped[int] = mapped_column(Integer, nullable=False)
    spend: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    revenue: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(18, 2))
    
    # Calculated metrics
    ctr: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 4))
    cpa: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    roas: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    
    # Bid information
    current_bid: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    bid_suggestion: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    
    # Classification
    category: Mapped[Optional[str]] = mapped_column(String(10))  # H, G, A, E, etc.
    intent: Mapped[Optional[str]] = mapped_column(String(50))  # informational, transactional
    
    performance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<KeywordPerformance(keyword={self.keyword}, ctr={self.ctr}, roas={self.roas})>"


class AgentExecutionHistory(Base):
    """Track agent execution history for audit and analysis."""
    
    __tablename__ = "agent_execution_history"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    agent_type: Mapped[str] = mapped_column(String(50), nullable=False)  # bid_strategy, content_brief, etc.
    
    # Execution details
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    input_data: Mapped[Optional[dict]] = mapped_column(JSON)
    output_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Performance metrics
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    cost_usd: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 6))
    
    # Outcome
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Context
    client_id: Mapped[Optional[str]] = mapped_column(String(36))
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36))
    
    execution_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<AgentExecutionHistory(agent={self.agent_name}, action={self.action}, success={self.success})>"


class ABTestCampaign(Base):
    """A/B test campaign definitions."""
    
    __tablename__ = "ab_test_campaigns"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    
    test_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Variants
    variant_a_campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"))
    variant_a_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variant_a_description: Mapped[Optional[str]] = mapped_column(String(500))
    
    variant_b_campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"))
    variant_b_name: Mapped[str] = mapped_column(String(100), nullable=False)
    variant_b_description: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Test configuration
    metric_to_optimize: Mapped[str] = mapped_column(String(50), nullable=False)  # roas, cpa, ctr, conversions
    test_duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    statistical_significance: Mapped[float] = mapped_column(Float, default=0.95)
    
    # Test status
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # planned, running, completed, paused
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Results
    winner: Mapped[Optional[str]] = mapped_column(String(20))  # variant_a, variant_b, inconclusive
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ABTestCampaign(name={self.test_name}, status={self.status}, winner={self.winner})>"


class ABTestResult(Base):
    """A/B test results and metrics."""
    
    __tablename__ = "ab_test_results"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    test_id: Mapped[str] = mapped_column(String(36), ForeignKey("ab_test_campaigns.id"), nullable=False, index=True)
    
    variant: Mapped[str] = mapped_column(String(20), nullable=False)  # variant_a or variant_b
    result_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Metrics
    impressions: Mapped[int] = mapped_column(Integer, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False)
    conversions: Mapped[int] = mapped_column(Integer, nullable=False)
    spend: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    revenue: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(18, 2))
    
    # Calculated metrics
    ctr: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 4))
    cpa: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    roas: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ABTestResult(test_id={self.test_id}, variant={self.variant}, roas={self.roas})>"


class ContentPerformanceByChannel(Base):
    """Track content performance across different channels."""
    
    __tablename__ = "content_performance_by_channel"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    content_id: Mapped[str] = mapped_column(String(36), ForeignKey("content_briefs.id"), nullable=False, index=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"))
    
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # meta, google, tiktok, etc.
    
    # Performance metrics
    impressions: Mapped[int] = mapped_column(Integer, nullable=False)
    clicks: Mapped[int] = mapped_column(Integer, nullable=False)
    engagements: Mapped[int] = mapped_column(Integer, nullable=False)
    conversions: Mapped[int] = mapped_column(Integer, nullable=False)
    spend: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    revenue: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(18, 2))
    
    # Engagement metrics
    likes: Mapped[Optional[int]] = mapped_column(Integer)
    shares: Mapped[Optional[int]] = mapped_column(Integer)
    comments: Mapped[Optional[int]] = mapped_column(Integer)
    video_views: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Audience demographics
    audience_age_distribution: Mapped[Optional[dict]] = mapped_column(JSON)
    audience_gender_distribution: Mapped[Optional[dict]] = mapped_column(JSON)
    audience_location_distribution: Mapped[Optional[dict]] = mapped_column(JSON)
    
    performance_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ContentPerformanceByChannel(content_id={self.content_id}, platform={self.platform}, roas={self.revenue/self.spend if self.spend else 0})>"