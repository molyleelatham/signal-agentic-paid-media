"""
Analytics and optimization models.
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import DECIMAL, DateTime, Date, ForeignKey, String, JSON, Integer, Boolean
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


class FunnelStage(Base):
    """Marketing funnel stage definitions."""
    
    __tablename__ = "funnel_stages"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # awareness, consideration, performance
    description: Mapped[Optional[str]] = mapped_column(String(255))
    risk_level: Mapped[str] = mapped_column(String(20), nullable=False)  # low, medium, high
    expected_roi_min: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    expected_roi_max: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    time_to_conversion: Mapped[str] = mapped_column(String(20))  # short, medium, long
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<FunnelStage(name={self.name}, risk_level={self.risk_level})>"


class ChannelMapping(Base):
    """Mapping of marketing channels to funnel stages."""
    
    __tablename__ = "channel_mappings"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    channel_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)  # meta, google, tiktok, etc.
    funnel_stage_id: Mapped[str] = mapped_column(String(36), ForeignKey("funnel_stages.id"), nullable=False)
    default_allocation_weight: Mapped[float] = mapped_column(DECIMAL(5, 4), nullable=False)  # Weight within funnel stage
    typical_cpa: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    typical_conversion_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 4))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ChannelMapping(channel={self.channel_name}, funnel_stage_id={self.funnel_stage_id})>"


class ScenarioModel(Base):
    """Saved scenario modeling configurations."""
    
    __tablename__ = "scenario_models"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Funnel allocation
    awareness_allocation: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    consideration_allocation: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    performance_allocation: Mapped[float] = mapped_column(DECIMAL(5, 2), nullable=False)
    
    # Scenario parameters
    total_budget: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    selected_channels: Mapped[Optional[dict]] = mapped_column(JSON)  # List of channel names
    
    # Results
    expected_leads: Mapped[Optional[int]] = mapped_column(Integer)
    expected_revenue: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(18, 2))
    expected_roas: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    risk_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    confidence: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 4))
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ScenarioModel(name={self.name}, client_id={self.client_id})>"


class OfflineCost(Base):
    """Offline marketing costs (OOH, events, sponsorships, etc.)."""
    
    __tablename__ = "offline_costs"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"))
    
    cost_type: Mapped[str] = mapped_column(String(50), nullable=False)  # ooh, event, sponsorship, print, etc.
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500))
    
    amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    
    # Expected impact
    expected_impressions: Mapped[Optional[int]] = mapped_column(Integer)
    expected_leads: Mapped[Optional[int]] = mapped_column(Integer)
    
    funnel_stage_id: Mapped[str] = mapped_column(String(36), ForeignKey("funnel_stages.id"), nullable=False)
    
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<OfflineCost(name={self.name}, cost_type={self.cost_type}, amount={self.amount})>"


class PerformanceMetric(Base):
    """Performance metrics tracking."""
    
    __tablename__ = "performance_metrics"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"))
    
    metric_name: Mapped[str] = mapped_column(String(100), nullable=False)
    metric_value: Mapped[Decimal] = mapped_column(DECIMAL(18, 4), nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<PerformanceMetric(name={self.metric_name}, value={self.metric_value}, date={self.metric_date})>"


class BudgetAllocation(Base):
    """Budget allocation records."""
    
    __tablename__ = "budget_allocations"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    campaign_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("campaigns.id"))
    
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    allocated_budget: Mapped[Decimal] = mapped_column(DECIMAL(18, 2), nullable=False)
    actual_spend: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(18, 2))
    
    allocation_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Thompson sampling parameters
    alpha: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 4))
    beta: Mapped[Optional[float]] = mapped_column(DECIMAL(10, 4))
    
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<BudgetAllocation(platform={self.platform}, budget={self.allocated_budget}, week={self.week})>"


class AttentionTokenTransaction(Base):
    """Attention token transaction records."""
    
    __tablename__ = "attention_token_transactions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    position_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("media_positions.id"))
    
    transaction_type: Mapped[str] = mapped_column(String(50), nullable=False)  # reward, penalty, stake, unstake, transfer
    amount: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(DECIMAL(18, 8), nullable=False)
    
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self) -> str:
        return f"<AttentionTokenTransaction(type={self.transaction_type}, amount={self.amount})>"


class EfficiencyMetrics(Base):
    """Efficiency metrics tracking."""
    
    __tablename__ = "efficiency_metrics"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    client_id: Mapped[str] = mapped_column(String(36), ForeignKey("clients.id"), nullable=False, index=True)
    
    # Current metrics
    current_cpl: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    current_roas: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    current_leads_per_week: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Previous metrics (before SIGNAL)
    previous_cpl: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2))
    previous_roas: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    previous_leads_per_week: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Business KPIs
    ltv_cac: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    retention_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 4))
    cart_abandonment_rate: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 4))
    
    # Improvement calculations
    cpl_improvement_percent: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    leads_improvement_percent: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    roas_improvement_percent: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    
    metric_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<EfficiencyMetrics(client_id={self.client_id}, cpl_improvement={self.cpl_improvement_percent})>"