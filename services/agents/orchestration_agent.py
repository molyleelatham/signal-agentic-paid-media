"""
Orchestration Agent - Central coordinator for all AI agents.

This agent coordinates the execution of specialized agents and manages
the overall decision-making flow for the SIGNAL platform.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

from shared.agents.overmind_integration import BaseAgent, OvermindTracer
from services.agents.content_brief_agent import ContentBriefAgent
from services.agents.bid_strategy_agent import BidStrategyAgent
from services.agents.market_analysis_agent import MarketAnalysisAgent
from services.agents.creative_optimization_agent import CreativeOptimizationAgent


class AgentPriority(Enum):
    """Priority levels for agent execution."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OrchestrationAgent(BaseAgent):
    """
    Central orchestration agent for SIGNAL platform.
    
    This agent:
    - Coordinates execution of specialized agents
    - Manages agent priorities and dependencies
    - Aggregates agent outputs into unified decisions
    - Handles agent failures and fallbacks
    - Provides overall system intelligence
    """
    
    def __init__(
        self,
        overmind_tracer: OvermindTracer = None,
        llm_client: Any = None,
        thrad_auction_integrator: Any = None
    ):
        """
        Initialize orchestration agent.
        
        Args:
            overmind_tracer: Overmind tracer instance
            llm_client: LLM client for orchestration decisions
            thrad_auction_integrator: Thrad auction integrator for bid orchestration
        """
        super().__init__(
            name="OrchestrationAgent",
            overmind_tracer=overmind_tracer,
            llm_client=llm_client
        )
        
        # Initialize specialized agents
        self.market_agent = MarketAnalysisAgent(overmind_tracer, llm_client)
        self.content_agent = ContentBriefAgent(overmind_tracer, llm_client)
        self.bid_agent = BidStrategyAgent(overmind_tracer, llm_client)
        self.creative_agent = CreativeOptimizationAgent(overmind_tracer, llm_client)
        
        # Initialize Thrad auction integrator
        self.thrad_auction = thrad_auction_integrator
        
        # Agent registry for dynamic execution
        self.agent_registry = {
            "market_analysis": self.market_agent,
            "content_brief": self.content_agent,
            "bid_strategy": self.bid_agent,
            "creative_optimization": self.creative_agent
        }
    
    async def orchestrate_thrad_auction(
        self,
        user_id: str,
        conversation_context: Dict,
        campaign_context: Dict = None
    ) -> Dict:
        """
        Orchestrate Thrad multi-bidder auction with agent strategic recommendations.
        
        This is the main entry point for ad serving, using Thrad's auction system
        instead of local bid discovery, while keeping agents for strategic enhancement.
        
        Args:
            user_id: User identifier
            conversation_context: Conversation context and messages
            campaign_context: Campaign context and goals
        
        Returns:
            Auction result with Thrad bid and agent insights
        """
        if not self.thrad_auction:
            raise ValueError("Thrad auction integrator not initialized")
        
        # Store context in memory
        self.memory.store("user_id", user_id)
        self.memory.store("conversation_context", conversation_context)
        self.memory.store("campaign_context", campaign_context or {})
        
        # Step 1: Market Analysis (for strategic recommendations)
        market_insights = await self._execute_agent_with_fallback(
            agent=self.market_agent,
            method="analyze_market_intelligence",
            method_args={
                "intelligence_data": conversation_context.get("intelligence_data", {}),
                "campaign_context": campaign_context or {},
                "historical_analysis": conversation_context.get("historical_analysis", [])
            },
            priority=AgentPriority.HIGH,
            fallback_value=[]
        )
        
        # Step 2: Generate agent strategic recommendations
        agent_recommendations = await self._generate_auction_recommendations(
            market_insights,
            campaign_context
        )
        
        # Step 3: Orchestrate Thrad auction with agent enhancements
        auction_result = await self.thrad_auction.orchestrate_auction(
            user_id=user_id,
            conversation_context=conversation_context,
            agent_recommendations=agent_recommendations
        )
        
        # Record orchestration decision
        self.memory.record_decision(
            agent_name=self.name,
            decision=f"Thrad auction {'won' if auction_result['bid']['won_bid'] else 'no bid'} for user {user_id}",
            reasoning=f"Auction orchestrated via Thrad multi-bidder system with {len(market_insights)} market insights",
            context={
                "user_id": user_id,
                "won_bid": auction_result['bid']['won_bid'],
                "auction_source": "thrad_multi_bidder"
            }
        )
        
        return auction_result
    
    async def _generate_auction_recommendations(
        self,
        market_insights: List,
        campaign_context: Dict
    ) -> Dict:
        """
        Generate strategic recommendations for Thrad auction.
        
        Args:
            market_insights: Market analysis results
            campaign_context: Campaign context
        
        Returns:
            Strategic recommendations for Thrad config
        """
        recommendations = {}
        
        # Extract strategic insights from market analysis
        if market_insights:
            high_priority_insights = [insight for insight in market_insights 
                                      if insight.urgency in ["high", "medium"]]
            
            if high_priority_insights:
                recommendations["market_priority"] = "high"
                recommendations["insight_count"] = len(high_priority_insights)
            else:
                recommendations["market_priority"] = "normal"
                recommendations["insight_count"] = len(market_insights)
        
        # Campaign-based recommendations
        if campaign_context:
            goal_type = campaign_context.get("goal", "")
            
            if goal_type == "brand_awareness":
                recommendations["ad_frequency_control"] = 3  # Less frequent for awareness
                recommendations["ad_offset"] = 2
            elif goal_type == "customer_acquisition":
                recommendations["ad_frequency_control"] = 1  # More aggressive
                recommendations["ad_offset"] = 1
            elif goal_type == "retargeting":
                recommendations["ad_frequency_control"] = 2
                recommendations["ad_offset"] = 0
        
        # Creative preferences based on campaign
        if campaign_context.get("creative_preferences"):
            recommendations["creative_preferences"] = campaign_context["creative_preferences"]
        
        # Experiment tag for A/B testing
        if campaign_context.get("experiment_id"):
            recommendations["experiment_tag"] = campaign_context["experiment_id"]
        
        return recommendations
    
    async def orchestrate_trading_decision(
        self,
        auction_context: Dict,
        campaign_context: Dict,
        intelligence_data: Dict,
        performance_history: List[Dict] = None
    ) -> Dict:
        """
        Orchestrate a complete trading decision using multiple agents.
        
        This is the main orchestration function - coordinates all agents
        to make a comprehensive trading decision.
        
        Args:
            auction_context: Current auction context
            campaign_context: Campaign context and goals
            intelligence_data: Market intelligence data
            performance_history: Performance history
        
        Returns:
            Comprehensive trading decision with all agent inputs
        """
        # Store orchestration context
        orchestration_context = {
            "auction_context": auction_context,
            "campaign_context": campaign_context,
            "intelligence_data": intelligence_data,
            "performance_history": performance_history or [],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.memory.store("orchestration_context", orchestration_context)
        
        # Step 1: Market Analysis (always run for context)
        market_insights = await self._execute_agent_with_fallback(
            agent=self.market_agent,
            method="analyze_market_intelligence",
            method_args={
                "intelligence_data": intelligence_data,
                "campaign_context": campaign_context,
                "historical_analysis": performance_history
            },
            priority=AgentPriority.HIGH,
            fallback_value=[]
        )
        
        # Step 2: Get algorithmic bid (from trading engine)
        algorithmic_bid = self._calculate_algorithmic_bid(
            auction_context,
            campaign_context,
            performance_history
        )
        
        # Step 3: Bid Strategy (uses market insights)
        bid_decision = await self._execute_agent_with_fallback(
            agent=self.bid_agent,
            method="decide_bid",
            method_args={
                "auction_context": auction_context,
                "algorithmic_bid": algorithmic_bid,
                "campaign_context": campaign_context,
                "performance_history": performance_history
            },
            priority=AgentPriority.CRITICAL,
            fallback_value={
                "recommended_bid": algorithmic_bid,
                "confidence": 0.5,
                "reasoning": "Fallback to algorithmic bid",
                "risk_assessment": "Unknown - agent fallback",
                "alternative_strategies": [],
                "market_context": auction_context
            }
        )
        
        # Step 4: Creative Optimization (if creative data available)
        creative_analysis = None
        if "creative_data" in auction_context:
            creative_analysis = await self._execute_agent_with_fallback(
                agent=self.creative_agent,
                method="analyze_creative",
                method_args={
                    "creative_data": auction_context["creative_data"],
                    "performance_metrics": auction_context.get("creative_performance", {}),
                    "benchmark_data": auction_context.get("creative_benchmarks", {})
                },
                priority=AgentPriority.MEDIUM,
                fallback_value=None
            )
        
        # Step 5: Aggregate decision
        final_decision = self._aggregate_trading_decision(
            market_insights=market_insights,
            bid_decision=bid_decision,
            creative_analysis=creative_analysis,
            orchestration_context=orchestration_context
        )
        
        # Record orchestration decision
        self.memory.record_decision(
            agent_name=self.name,
            decision=f"Orchestrated trading decision: bid ${final_decision['final_bid']:.2f}",
            reasoning=f"Based on {len(market_insights)} market insights and bid strategy analysis",
            context=orchestration_context
        )
        
        return final_decision
    
    async def orchestrate_content_generation(
        self,
        gap_topics: List[Dict],
        campaign_context: Dict,
        platform: str
    ) -> Dict:
        """
        Orchestrate content brief generation for multiple gap topics.
        
        Args:
            gap_topics: List of gap topics from BERTopic analysis
            campaign_context: Campaign context
            platform: Target platform
        
        Returns:
            Content generation results with briefs
        """
        orchestration_context = {
            "gap_topics": gap_topics,
            "campaign_context": campaign_context,
            "platform": platform,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.memory.store("content_orchestration_context", orchestration_context)
        
        # Generate content briefs
        content_briefs = await self.content_agent.generate_multiple_briefs(
            gap_topics=gap_topics,
            platform=platform,
            goal_type=campaign_context.get("goal", "lead_generation"),
            max_briefs=5
        )
        
        # Evaluate brief quality
        evaluated_briefs = []
        for brief in content_briefs:
            quality = await self.content_agent.evaluate_brief_quality(
                brief=brief,
                gap_topic=next((t for t in gap_topics if t.get("name") == brief.topic), {})
            )
            evaluated_briefs.append({
                "brief": brief,
                "quality": quality
            })
        
        # Rank by quality
        ranked_briefs = sorted(
            evaluated_briefs,
            key=lambda x: x["quality"]["overall_score"],
            reverse=True
        )
        
        return {
            "briefs": ranked_briefs,
            "total_generated": len(content_briefs),
            "platform": platform,
            "orchestration_context": orchestration_context
        }
    
    async def orchestrate_daily_optimization(
        self,
        campaign_id: str,
        performance_data: Dict,
        intelligence_data: Dict,
        market_conditions: Dict
    ) -> Dict:
        """
        Orchestrate daily optimization routine.
        
        Args:
            campaign_id: Campaign identifier
            performance_data: Performance data
            intelligence_data: Market intelligence
            market_conditions: Current market conditions
        
        Returns:
            Optimization recommendations from all agents
        """
        orchestration_context = {
            "campaign_id": campaign_id,
            "performance_data": performance_data,
            "intelligence_data": intelligence_data,
            "market_conditions": market_conditions,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Market Analysis
        market_insights = await self.market_agent.analyze_market_intelligence(
            intelligence_data=intelligence_data,
            campaign_context={"goal": performance_data.get("goal", "unknown")},
            historical_analysis=performance_data.get("historical_analysis", [])
        )
        
        # Creative Optimization (for underperforming creatives)
        creative_recommendations = []
        for creative_id, creative_perf in performance_data.get("creatives", {}).items():
            if creative_perf.get("performance_score", 1.0) < 0.7:  # Underperforming
                analysis = await self.creative_agent.analyze_creative(
                    creative_data=creative_perf.get("data", {}),
                    performance_metrics=creative_perf.get("metrics", {}),
                    benchmark_data=performance_data.get("benchmarks", {})
                )
                creative_recommendations.append({
                    "creative_id": creative_id,
                    "analysis": analysis
                })
        
        # Bid Strategy Optimization
        bid_optimization = await self.bid_agent.optimize_bidding_strategy(
            performance_data=performance_data.get("bid_history", []),
            market_conditions=market_conditions
        )
        
        return {
            "market_insights": market_insights,
            "creative_recommendations": creative_recommendations,
            "bid_optimization": bid_optimization,
            "orchestration_context": orchestration_context
        }
    
    def _calculate_algorithmic_bid(
        self,
        auction_context: Dict,
        campaign_context: Dict,
        performance_history: List[Dict]
    ) -> float:
        """
        Calculate algorithmic bid using trading engine components.
        
        This would integrate with the LOESS/DMR and Bayesian components
        implemented earlier.
        
        Args:
            auction_context: Auction context
            campaign_context: Campaign context
            performance_history: Performance history
        
        Returns:
            Algorithmic bid suggestion
        """
        # Placeholder - would integrate with actual trading engine
        base_bid = auction_context.get("base_bid", 1.0)
        competition_multiplier = {
            "low": 0.9,
            "medium": 1.0,
            "high": 1.1
        }.get(auction_context.get("competition_level", "medium"), 1.0)
        
        return base_bid * competition_multiplier
    
    async def _execute_agent_with_fallback(
        self,
        agent: BaseAgent,
        method: str,
        method_args: Dict,
        priority: AgentPriority,
        fallback_value: Any
    ) -> Any:
        """
        Execute agent method with fallback on failure.
        
        Args:
            agent: Agent instance
            method: Method name to call
            method_args: Method arguments
            priority: Execution priority
            fallback_value: Fallback value if execution fails
        
        Returns:
            Agent method result or fallback value
        """
        try:
            agent_method = getattr(agent, method)
            return await agent_method(**method_args)
        except Exception as e:
            print(f"Agent {agent.name} method {method} failed: {e}")
            print(f"Using fallback value for priority {priority.value}")
            return fallback_value
    
    def _aggregate_trading_decision(
        self,
        market_insights: List,
        bid_decision: Dict,
        creative_analysis: Any,
        orchestration_context: Dict
    ) -> Dict:
        """
        Aggregate agent outputs into unified trading decision.
        
        Args:
            market_insights: Market analysis results
            bid_decision: Bid strategy decision
            creative_analysis: Creative analysis results
            orchestration_context: Full orchestration context
        
        Returns:
            Aggregated trading decision
        """
        return {
            "final_bid": bid_decision["recommended_bid"],
            "bid_confidence": bid_decision["confidence"],
            "bid_reasoning": bid_decision["reasoning"],
            "risk_assessment": bid_decision["risk_assessment"],
            "market_insights_count": len(market_insights),
            "market_insights_summary": [insight.summary for insight in market_insights[:3]],
            "creative_analysis_available": creative_analysis is not None,
            "creative_performance_score": creative_analysis.performance_score if creative_analysis else None,
            "orchestration_timestamp": orchestration_context["timestamp"],
            "agents_executed": ["market_analysis", "bid_strategy"] + (["creative_optimization"] if creative_analysis else []),
            "decision_source": "orchestrated_agent_decision"
        }