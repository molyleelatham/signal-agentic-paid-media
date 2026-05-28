"""
Bloomberg Terminal-style API Routes
Optimized for real-time marketing agent dashboard
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from datetime import datetime, timedelta
import random
import numpy as np

router = APIRouter(prefix="/terminal", tags=["terminal"])


# ============ MODELS ============

class ChannelMetric(BaseModel):
    name: str
    spend: float
    leads: int
    cpa: float
    trend: Literal["up", "down"]


class CampaignSignal(BaseModel):
    name: str
    signal: Literal["BUY", "HOLD", "STOP"]
    confidence: float
    spend: float
    roas: float


class AdstockSaturation(BaseModel):
    channel: str
    saturation: float
    days_until_refresh: int
    signal: Literal["HOLD", "REFRESH"]


class FunnelSegment(BaseModel):
    awareness: float
    consideration: float
    performance: float


class TimelineData(BaseModel):
    month: str
    value: float


class Scenario(BaseModel):
    name: Literal["conservative", "moderate", "growth"]
    roas: float
    risk_level: Literal["low", "medium", "high"]
    pillar_allocation: Dict[str, float]
    channel_allocation: Dict[str, float]
    expected_return: float


class IntelligenceResult(BaseModel):
    topic: str
    source: Literal["TAVILY", "BERT"]
    relevance: float
    classification: str


class ContentGap(BaseModel):
    topic: str
    severity: Literal["high", "medium", "low"]
    gap_score: float


class AlgorithmScore(BaseModel):
    name: str
    score: float
    status: Literal["optimal", "good", "needs_attention"]


class AgentLog(BaseModel):
    timestamp: str
    agent: str
    action: str
    result: Optional[str] = None


class StrategyDoc(BaseModel):
    previous_strategy: str
    agent_actions: List[str]
    algorithm_results: Dict[str, str]
    fine_tuning_applied: List[str]
    last_updated: str


class HeaderStats(BaseModel):
    budget: float
    leads: int
    roas: float
    tokens: int


# ============ DEMO DATA GENERATOR ============

class DemoDataGenerator:
    """Generates realistic but flexible demo data for terminal UI"""
    
    CHANNELS = ["META", "GOOGLE", "TIKTOK", "MICROSOFT", "REDDIT", "LINKEDIN"]
    FUNNEL_STAGES = ["awareness", "consideration", "performance"]
    
    @staticmethod
    def generate_channel_metrics() -> List[ChannelMetric]:
        """Generate channel metrics with realistic trends"""
        return [
            ChannelMetric(
                name=channel,
                spend=random.uniform(2000, 15000),
                leads=random.randint(50, 500),
                cpa=random.uniform(20, 50),
                trend=random.choice(["up", "down"])
            )
            for channel in DemoDataGenerator.CHANNELS
        ]
    
    @staticmethod
    def generate_campaign_signals() -> List[CampaignSignal]:
        """Generate campaign signals with realistic confidence scores"""
        campaigns = [
            "Summer Collection 2025",
            "Brand Awareness Q2",
            "Retargeting Pool A",
            "Seasonal Push",
            "Lookalike Expansion"
        ]
        
        signals = []
        for campaign in campaigns:
            signal = random.choice(["BUY", "HOLD", "STOP"])
            # BUY signals have higher confidence
            base_confidence = random.uniform(65, 95) if signal == "BUY" else random.uniform(60, 85)
            
            signals.append(CampaignSignal(
                name=campaign,
                signal=signal,
                confidence=round(base_confidence, 1),
                spend=random.uniform(3000, 12000),
                roas=random.uniform(1.5, 4.5)
            ))
        
        return signals
    
    @staticmethod
    def generate_adstock_saturation() -> List[AdstockSaturation]:
        """Generate adstock saturation levels"""
        return [
            AdstockSaturation(
                channel=channel,
                saturation=random.uniform(0.4, 0.95),
                days_until_refresh=random.randint(1, 14),
                signal="REFRESH" if random.random() > 0.7 else "HOLD"
            )
            for channel in DemoDataGenerator.CHANNELS[:4]
        ]
    
    @staticmethod
    def generate_funnel_data(mode: str) -> FunnelSegment:
        """Generate funnel data for different modes (leads/revenue/spend)"""
        if mode == "leads":
            base = random.uniform(200, 300)
            awareness = base * random.uniform(1.2, 1.5)
            consideration = base * random.uniform(0.8, 1.0)
            performance = base * random.uniform(0.3, 0.5)
        
        elif mode == "revenue":
            base = random.uniform(40000, 60000)
            awareness = base * random.uniform(0.7, 0.9)
            consideration = base * random.uniform(1.5, 2.2)
            performance = base * random.uniform(1.8, 2.5)
        
        else:  # spend
            base = random.uniform(8000, 15000)
            awareness = base * random.uniform(0.5, 0.7)
            consideration = base * random.uniform(0.8, 1.2)
            performance = base * random.uniform(0.9, 1.3)
        
        return FunnelSegment(
            awareness=round(awareness, 2),
            consideration=round(consideration, 2),
            performance=round(performance, 2)
        )
    
    @staticmethod
    def generate_timeline_data() -> List[TimelineData]:
        """Generate 12-month timeline data"""
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        base_value = random.uniform(60, 80)
        
        timeline = []
        for i, month in enumerate(months):
            # Add trend and seasonality
            trend = i * 2  # Upward trend
            seasonality = 10 * np.sin(i * 0.5)  # Seasonal fluctuation
            value = base_value + trend + seasonality + random.uniform(-5, 5)
            timeline.append(TimelineData(month=month, value=round(max(50, value), 1)))
        
        return timeline
    
    @staticmethod
    def generate_scenarios() -> Dict[str, Scenario]:
        """Generate three budget allocation scenarios"""
        return {
            "conservative": Scenario(
                name="conservative",
                roas=2.1,
                risk_level="low",
                pillar_allocation={"awareness": 35, "consideration": 40, "performance": 25},
                channel_allocation={
                    "meta": 30, "google": 25, "tiktok": 20, 
                    "microsoft": 15, "reddit": 5, "linkedin": 5
                },
                expected_return=73500
            ),
            "moderate": Scenario(
                name="moderate",
                roas=3.2,
                risk_level="medium",
                pillar_allocation={"awareness": 25, "consideration": 35, "performance": 40},
                channel_allocation={
                    "meta": 25, "google": 30, "tiktok": 25,
                    "microsoft": 10, "reddit": 5, "linkedin": 5
                },
                expected_return=112000
            ),
            "growth": Scenario(
                name="growth",
                roas=4.8,
                risk_level="high",
                pillar_allocation={"awareness": 20, "consideration": 30, "performance": 50},
                channel_allocation={
                    "meta": 20, "google": 35, "tiktok": 30,
                    "microsoft": 10, "reddit": 3, "linkedin": 2
                },
                expected_return=168000
            )
        }
    
    @staticmethod
    def generate_intelligence_results(query: str = "") -> List[IntelligenceResult]:
        """Generate intelligence results from Tavily/BERT"""
        topics = [
            f"Summer fitness trends 2025",
            f"Gym workout equipment demand",
            f"Athleisure market growth",
            f"Consumer sentiment on fitness apps"
        ]
        
        return [
            IntelligenceResult(
                topic=topic,
                source=random.choice(["TAVILY", "BERT"]),
                relevance=random.uniform(0.75, 0.95),
                classification=random.choice(["H", "G", "A"])  # DisBERT classification
            )
            for topic in topics
        ]
    
    @staticmethod
    def generate_content_gaps() -> List[ContentGap]:
        """Generate content gap analysis"""
        topics = [
            "Summer workout routines",
            "Nutrition guides",
            "Athlete testimonials",
            "Training equipment reviews",
            "Recovery tips"
        ]
        
        return [
            ContentGap(
                topic=topic,
                severity=random.choice(["high", "medium", "low"]),
                gap_score=random.uniform(30, 95)
            )
            for topic in topics
        ]
    
    @staticmethod
    def generate_algorithm_scores() -> List[AlgorithmScore]:
        """Generate real-time algorithm performance scores"""
        algorithms = [
            ("THOMPSON", "Thompson sampling optimization"),
            ("SPLINE", "Spline interpolation predictions"),
            ("ADSTOCK", "Adstock decay model"),
            ("OVERMIND", "Overmind evaluation system"),
            ("BERT", "BERT keyword classification"),
            ("TOKENS", "Token reward calculation")
        ]
        
        return [
            AlgorithmScore(
                name=name,
                score=random.uniform(75, 95),
                status=random.choice(["optimal", "good", "needs_attention"])
            )
            for name, _ in algorithms
        ]
    
    @staticmethod
    def generate_agent_logs(limit: int = 20) -> List[AgentLog]:
        """Generate agent action logs for CLI display"""
        agents = [
            "THOMPSON_ALLOCATOR",
            "ADSTOCK_ENGINE",
            "OVERMIND_TRACER",
            "BERT_CLIENT",
            "TAVILY_CLIENT",
            "TOKEN_CALCULATOR",
            "MEDIA_BUYER"
        ]
        
        actions = [
            "Optimizing channel allocations...",
            "Monitoring saturation levels...",
            "Evaluating scenario performance...",
            "Analyzing keyword performance...",
            "Retrieving market intelligence...",
            "Computing reward distribution...",
            "Executing campaign adjustments..."
        ]
        
        logs = []
        now = datetime.now()
        
        for i in range(limit):
            timestamp = (now - timedelta(seconds=random.randint(0, 3600))).strftime("%H:%M:%S")
            logs.append(AgentLog(
                timestamp=timestamp,
                agent=random.choice(agents),
                action=random.choice(actions),
                result=random.choice(["Success", "Optimized", "Complete", "Updated"])
            ))
        
        return sorted(logs, key=lambda x: x.timestamp, reverse=True)
    
    @staticmethod
    def generate_strategy_docs() -> StrategyDoc:
        """Generate strategy documentation"""
        return StrategyDoc(
            previous_strategy="Q2 2025: Focus on brand awareness with 60% allocation to top-funnel channels",
            agent_actions=[
                "Thompson sampling optimized Meta allocation from 35% to 30%",
                "Adstock model triggered creative refresh for Google (91% saturation)",
                "Overmind evaluation increased confidence score from 72% to 87%",
                "BERT keyword analysis added 15 high-intent keywords"
            ],
            algorithm_results={
                "thompson": "Beta-Bernoulli bandit converged with 87% confidence",
                "spline": "Cubic spline predictions achieved 92% accuracy",
                "adstock": "Decay rate calibration reduced false positives by 23%"
            },
            fine_tuning_applied=[
                "Adjusted lambda decay parameter from 0.7 to 0.75 for Meta",
                "Increased exploration budget from 10% to 15% for TikTok",
                "Updated Overmind weights: leads 50%, CPA 30%, score 20%"
            ],
            last_updated=datetime.now().isoformat()
        )
    
    @staticmethod
    def generate_header_stats() -> HeaderStats:
        """Generate header statistics"""
        return HeaderStats(
            budget=random.uniform(30000, 40000),
            leads=random.randint(1000, 1500),
            roas=random.uniform(2.5, 4.0),
            tokens=random.randint(700, 1000)
        )


# ============ ENDPOINTS ============

@router.get("/header-stats")
async def get_header_stats() -> HeaderStats:
    """Get real-time header statistics (budget, leads, ROAS, tokens)"""
    return DemoDataGenerator.generate_header_stats()


@router.get("/channel-metrics")
async def get_channel_metrics() -> List[ChannelMetric]:
    """Get channel performance metrics with trends"""
    return DemoDataGenerator.generate_channel_metrics()


@router.get("/campaign-signals")
async def get_campaign_signals() -> List[CampaignSignal]:
    """Get campaign signals (BUY/HOLD/STOP) with confidence scores"""
    return DemoDataGenerator.generate_campaign_signals()


@router.get("/adstock-saturation")
async def get_adstock_saturation() -> List[AdstockSaturation]:
    """Get adstock saturation levels and refresh signals"""
    return DemoDataGenerator.generate_adstock_saturation()


@router.get("/strategy-brief")
async def get_strategy_brief(mode: Literal["leads", "revenue", "spend"] = "leads"):
    """Get strategy brief funnel data by mode"""
    funnel_data = DemoDataGenerator.generate_funnel_data(mode)
    timeline_data = DemoDataGenerator.generate_timeline_data()
    
    return {
        "mode": mode,
        "funnel": funnel_data,
        "timeline": timeline_data
    }


@router.get("/strategy-docs")
async def get_strategy_docs() -> StrategyDoc:
    """Get strategy documentation (previous strategy, actions, results)"""
    return DemoDataGenerator.generate_strategy_docs()


@router.get("/budget-scenarios")
async def get_budget_scenarios() -> Dict[str, Scenario]:
    """Get three budget allocation scenarios (conservative/moderate/growth)"""
    return DemoDataGenerator.generate_scenarios()


@router.get("/budget-scenarios/{scenario_name}")
async def get_scenario_detail(scenario_name: Literal["conservative", "moderate", "growth"]) -> Scenario:
    """Get detailed information for a specific scenario"""
    scenarios = DemoDataGenerator.generate_scenarios()
    if scenario_name not in scenarios:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return scenarios[scenario_name]


@router.get("/intelligence-results")
async def get_intelligence_results(query: str = "") -> List[IntelligenceResult]:
    """Get intelligence results from Tavily/BERT with classification"""
    return DemoDataGenerator.generate_intelligence_results(query)


@router.get("/content-gaps")
async def get_content_gaps() -> List[ContentGap]:
    """Get content gap matrix analysis"""
    return DemoDataGenerator.generate_content_gaps()


@router.get("/algorithm-scores")
async def get_algorithm_scores() -> List[AlgorithmScore]:
    """Get real-time algorithm performance scores"""
    return DemoDataGenerator.generate_algorithm_scores()


@router.get("/agent-logs")
async def get_agent_logs(limit: int = 20) -> List[AgentLog]:
    """Get agent action logs for CLI display"""
    return DemoDataGenerator.generate_agent_logs(limit)


@router.get("/full-dashboard")
async def get_full_dashboard():
    """Get all dashboard data in a single request (optimized for initial load)"""
    return {
        "header_stats": DemoDataGenerator.generate_header_stats(),
        "channel_metrics": DemoDataGenerator.generate_channel_metrics(),
        "campaign_signals": DemoDataGenerator.generate_campaign_signals(),
        "adstock_saturation": DemoDataGenerator.generate_adstock_saturation(),
        "strategy_brief": {
            "leads": DemoDataGenerator.generate_funnel_data("leads"),
            "revenue": DemoDataGenerator.generate_funnel_data("revenue"),
            "spend": DemoDataGenerator.generate_funnel_data("spend"),
            "timeline": DemoDataGenerator.generate_timeline_data()
        },
        "strategy_docs": DemoDataGenerator.generate_strategy_docs(),
        "budget_scenarios": DemoDataGenerator.generate_scenarios(),
        "intelligence_results": DemoDataGenerator.generate_intelligence_results(),
        "content_gaps": DemoDataGenerator.generate_content_gaps(),
        "algorithm_scores": DemoDataGenerator.generate_algorithm_scores(),
        "agent_logs": DemoDataGenerator.generate_agent_logs(20)
    }