"""
Bid Strategy Agent.

This agent uses LLM to make strategic bidding decisions.
Integrates with Overmind for tracing and optimization.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

from shared.agents.overmind_integration import BaseAgent, OvermindTracer
from shared.agents.cursor_integration import CursorComposerService


@dataclass
class BidDecision:
    """Agent-generated bid decision."""
    
    recommended_bid: float
    confidence: float
    reasoning: str
    risk_assessment: str
    alternative_strategies: List[str]
    market_context: Dict


class BidStrategyAgent(BaseAgent):
    """
    Bid Strategy Agent.
    
    This agent:
    - Analyzes market conditions and competitive landscape
    - Makes strategic bidding decisions beyond algorithmic calculations
    - Provides reasoning and risk assessment for bid decisions
    - Suggests alternative strategies
    """
    
    def __init__(
        self,
        overmind_tracer: OvermindTracer = None,
        llm_client: Any = None,
        cursor_composer: CursorComposerService = None,
    ):
        """
        Initialize bid strategy agent.
        
        Args:
            overmind_tracer: Overmind tracer instance
            llm_client: LLM client for decision making
            cursor_composer: Cursor Composer 2.5 service
        """
        super().__init__(
            name="BidStrategyAgent",
            overmind_tracer=overmind_tracer,
            llm_client=llm_client,
            cursor_composer=cursor_composer,
        )
    
    async def decide_bid(
        self,
        auction_context: Dict,
        algorithmic_bid: float,
        campaign_context: Dict,
        performance_history: List[Dict] = None
    ) -> BidDecision:
        """
        Make a strategic bid decision for an auction.
        
        This is the main agent function - uses LLM to make nuanced bidding decisions
        that go beyond pure algorithmic calculations.
        
        Args:
            auction_context: Current auction context (platform, competition, etc.)
            algorithmic_bid: Bid suggested by algorithmic components (LOESS, etc.)
            campaign_context: Campaign goals, budget, constraints
            performance_history: Recent performance data
        
        Returns:
            Strategic bid decision with reasoning
        """
        # Store context in memory
        self.memory.store("auction_context", auction_context)
        self.memory.store("algorithmic_bid", algorithmic_bid)
        self.memory.store("campaign_context", campaign_context)
        self.memory.store("performance_history", performance_history or [])
        
        # Build prompt for LLM
        prompt = self._build_bid_decision_prompt(
            auction_context,
            algorithmic_bid,
            campaign_context,
            performance_history
        )
        
        # Call LLM for strategic decision (with Overmind tracing)
        response = await self.think(
            prompt=prompt,
            context={
                "auction_context": auction_context,
                "algorithmic_bid": algorithmic_bid,
                "campaign_context": campaign_context
            }
        )
        
        # Parse LLM response into structured decision
        decision = self._parse_bid_decision(response, algorithmic_bid, auction_context)
        
        # Record decision
        self.memory.record_decision(
            agent_name=self.name,
            decision=f"Bid ${decision.recommended_bid:.2f} for {auction_context.get('platform', 'unknown')}",
            reasoning=decision.reasoning,
            context={
                "auction_context": auction_context,
                "algorithmic_bid": algorithmic_bid,
                "final_bid": decision.recommended_bid
            }
        )
        
        return decision
    
    def _build_bid_decision_prompt(
        self,
        auction_context: Dict,
        algorithmic_bid: float,
        campaign_context: Dict,
        performance_history: List[Dict]
    ) -> str:
        """
        Build prompt for bid decision.
        
        Args:
            auction_context: Auction context
            algorithmic_bid: Algorithmic bid suggestion
            campaign_context: Campaign context
            performance_history: Performance history
        
        Returns:
            LLM prompt
        """
        platform = auction_context.get("platform", "unknown")
        competition_level = auction_context.get("competition_level", "medium")
        time_of_day = auction_context.get("time_of_day", "unknown")
        
        goal = campaign_context.get("goal", "unknown")
        budget_remaining = campaign_context.get("budget_remaining", 0)
        urgency = campaign_context.get("urgency", "normal")
        
        performance_summary = ""
        if performance_history:
            recent_performance = performance_history[-5:]  # Last 5 data points
            avg_ctr = sum(p.get("ctr", 0) for p in recent_performance) / len(recent_performance)
            avg_conv_rate = sum(p.get("conversion_rate", 0) for p in recent_performance) / len(recent_performance)
            performance_summary = f"""
Recent Performance:
- Average CTR: {avg_ctr:.2%}
- Average Conversion Rate: {avg_conv_rate:.2%}
"""
        
        prompt = f"""You are an expert media trading strategist. Make a bid decision for this auction:

ALGORITHMIC RECOMMENDATION: ${algorithmic_bid:.2f}

AUCTION CONTEXT:
- Platform: {platform}
- Competition Level: {competition_level}
- Time of Day: {time_of_day}

CAMPAIGN CONTEXT:
- Goal: {goal}
- Budget Remaining: ${budget_remaining:.2f}
- Urgency: {urgency}
{performance_summary}

Analyze the situation and decide:
1. Should we follow, increase, or decrease the algorithmic bid?
2. What is your recommended bid amount?
3. What is your reasoning?
4. What are the risks?
5. What alternative strategies would you consider?

Provide specific bid amount and detailed reasoning."""
        
        return prompt
    
    def _parse_bid_decision(
        self,
        response: str,
        algorithmic_bid: float,
        auction_context: Dict
    ) -> BidDecision:
        """
        Parse LLM response into structured bid decision.
        
        Args:
            response: LLM response text
            algorithmic_bid: Original algorithmic bid
            auction_context: Auction context
        
        Returns:
            Structured bid decision
        """
        # In production, this would properly parse the LLM response
        # For now, use algorithmic bid with agent reasoning
        
        # Simple logic: adjust based on competition
        competition_level = auction_context.get("competition_level", "medium")
        
        if competition_level == "high":
            adjustment_factor = 1.1  # Increase bid by 10%
            risk_assessment = "High competition - increased bid to win impression"
        elif competition_level == "low":
            adjustment_factor = 0.9  # Decrease bid by 10%
            risk_assessment = "Low competition - reduced bid to improve efficiency"
        else:
            adjustment_factor = 1.0
            risk_assessment = "Normal competition - following algorithmic recommendation"
        
        recommended_bid = algorithmic_bid * adjustment_factor
        
        return BidDecision(
            recommended_bid=recommended_bid,
            confidence=0.82,
            reasoning=response[:500] if response else f"Adjusted algorithmic bid by {adjustment_factor:.0%} based on competition level",
            risk_assessment=risk_assessment,
            alternative_strategies=[
                "Wait for lower competition periods",
                "Focus on different audience segments",
                "Adjust creative to improve conversion rate"
            ],
            market_context=auction_context
        )
    
    async def analyze_bid_outcome(
        self,
        bid_decision: BidDecision,
        actual_outcome: Dict
    ) -> Dict:
        """
        Analyze the outcome of a bid decision for learning.
        
        Args:
            bid_decision: The bid decision that was made
            actual_outcome: Actual auction outcome (won/lost, cost, performance)
        
        Returns:
            Analysis of decision quality
        """
        outcome_analysis = {
            "bid_won": actual_outcome.get("won", False),
            "actual_cost": actual_outcome.get("cost", 0),
            "performance": actual_outcome.get("performance", {}),
            "bid_accuracy": abs(bid_decision.recommended_bid - actual_outcome.get("winning_bid", bid_decision.recommended_bid)),
            "reasoning_quality": "Good" if actual_outcome.get("won") else "Needs improvement"
        }
        
        # Store in long-term memory
        self.memory.store(
            f"bid_outcome_{datetime.utcnow().timestamp()}",
            {
                "decision": bid_decision.__dict__,
                "outcome": actual_outcome,
                "analysis": outcome_analysis
            },
            memory_type="long"
        )
        
        # Log to Overmind for optimization
        if self.overmind_tracer.client:
            performance_score = 1.0 if actual_outcome.get("won") else 0.5
            self.overmind_tracer.log_outcome(
                trace_id=f"bid_{datetime.utcnow().timestamp()}",
                outcome_label="bid_success",
                outcome_value=performance_score
            )
        
        return outcome_analysis
    
    async def optimize_bidding_strategy(
        self,
        performance_data: List[Dict],
        market_conditions: Dict
    ) -> Dict:
        """
        Optimize overall bidding strategy based on performance.
        
        Args:
            performance_data: Historical performance data
            market_conditions: Current market conditions
        
        Returns:
            Optimized strategy recommendations
        """
        prompt = f"""Analyze the following performance data and optimize bidding strategy:

PERFORMANCE DATA (Last 30 days):
{self._format_performance_data(performance_data)}

CURRENT MARKET CONDITIONS:
{self._format_market_conditions(market_conditions)}

Provide recommendations for:
1. Overall bid level adjustments
2. Platform-specific strategies
3. Time-of-day optimization
4. Audience segment focusing
5. Risk management improvements"""
        
        optimization = await self.think(
            prompt=prompt,
            context={
                "performance_data": performance_data,
                "market_conditions": market_conditions
            }
        )
        
        return {
            "recommendations": optimization,
            "confidence": 0.75,
            "data_points_analyzed": len(performance_data)
        }
    
    def _format_performance_data(self, performance_data: List[Dict]) -> str:
        """Format performance data for prompt."""
        if not performance_data:
            return "No performance data available"
        
        summary = {
            "total_impressions": sum(p.get("impressions", 0) for p in performance_data),
            "total_conversions": sum(p.get("conversions", 0) for p in performance_data),
            "total_spend": sum(p.get("spend", 0) for p in performance_data),
            "avg_ctr": sum(p.get("ctr", 0) for p in performance_data) / len(performance_data),
        }
        
        return str(summary)
    
    def _format_market_conditions(self, market_conditions: Dict) -> str:
        """Format market conditions for prompt."""
        return str(market_conditions)