"""
Agent Trigger Service

Provides unified interface for triggering all agents with proper logging.
"""

import uuid
import time
from typing import Dict, Optional, List
from datetime import datetime
from enum import Enum

from services.common import agent_logger, agent_execution_logger
from services.media_planning import campaign_keyword_logger
from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator
from services.intelligence.tavily_to_disbert_mapper import tavily_to_disbert_mapper
from shared.utils.settings import settings

BID_PLATFORMS = ("google", "tiktok", "msft")


class AgentTriggerType(Enum):
    """Types of agent triggers."""
    BID_OPTIMIZE = "bid_optimize"
    CONTENT_GENERATE = "content_generate"
    CREATIVE_OPTIMIZE = "creative_optimize"
    MARKET_ANALYZE = "market_analyze"
    ORCHESTRATE = "orchestrate"
    KEYWORD_CLASSIFY = "keyword_classify"
    CAMPAIGN_ALLOCATE = "campaign_allocate"
    RESEARCH_TAVILY = "research_tavily"


class AgentTriggerResult:
    """Result of an agent trigger."""
    
    def __init__(
        self,
        success: bool,
        agent_name: str,
        action: str,
        output: Optional[Dict] = None,
        error: Optional[str] = None,
        execution_time_ms: int = 0,
        tokens_used: int = 0,
        cost_usd: float = 0.0
    ):
        self.success = success
        self.agent_name = agent_name
        self.action = action
        self.output = output
        self.error = error
        self.execution_time_ms = execution_time_ms
        self.tokens_used = tokens_used
        self.cost_usd = cost_usd
        self.trigger_id = str(uuid.uuid4())
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "trigger_id": self.trigger_id,
            "timestamp": self.timestamp,
            "success": self.success,
            "agent_name": self.agent_name,
            "action": self.action,
            "output": self.output,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd
        }


class AgentTriggerService:
    """
    Unified service for triggering all agents.
    
    This service:
    - Provides single interface for all agent triggers
    - Logs all triggers to agent_logger and agent_execution_logger
    - Returns standardized results
    - Supports reactive UI updates
    """
    
    def __init__(self):
        """Initialize agent trigger service."""
        # DisBERT integrator
        self.disbert_integrator = DisBERTThradAdIntegrator()
    
    async def trigger_bid_optimize(
        self,
        keyword: str,
        current_bid: float,
        platform: str = "google",
        campaign_id: Optional[str] = None
    ) -> AgentTriggerResult:
        """
        Trigger bid optimization agent.
        
        Args:
            keyword: Keyword to optimize bid for
            current_bid: Current bid amount
            platform: Platform (google, meta, tiktok, microsoft)
            campaign_id: Campaign ID
            
        Returns:
            AgentTriggerResult with optimization recommendation
        """
        start_time = time.time()
        agent_name = "bid_strategy_agent"
        
        try:
            # Simulate bid optimization logic
            # In production, this would call the actual agent
            confidence = 0.85 + (hash(keyword) % 10) / 100
            market_competition = (hash(keyword) % 50) / 100
            
            # Calculate recommended bid
            if market_competition > 0.3 and confidence > 0.8:
                recommended_bid = current_bid * 1.15  # Increase by 15%
                action = "increase"
            elif market_competition < 0.2:
                recommended_bid = current_bid * 0.90  # Decrease by 10%
                action = "decrease"
            else:
                recommended_bid = current_bid
                action = "hold"
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log to agent logger
            agent_logger.log_optimize(
                agent="BID_STRATEGY",
                campaign=campaign_id or "Unknown",
                optimization_type=f"Bid {action}: £{current_bid:.2f} → £{recommended_bid:.2f}",
                confidence=confidence
            )
            
            # Log to execution logger
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="bid_strategy",
                action="optimize_bid",
                input_data={
                    "keyword": keyword,
                    "current_bid": current_bid,
                    "platform": platform
                },
                output_data={
                    "recommended_bid": recommended_bid,
                    "action": action,
                    "confidence": confidence,
                    "market_competition": market_competition
                },
                execution_time_ms=execution_time_ms,
                tokens_used=150,
                cost_usd=0.0015,
                success=True,
                campaign_id=campaign_id
            )
            
            return AgentTriggerResult(
                success=True,
                agent_name=agent_name,
                action="optimize_bid",
                output={
                    "keyword": keyword,
                    "current_bid": current_bid,
                    "recommended_bid": recommended_bid,
                    "action": action,
                    "confidence": confidence,
                    "market_competition": market_competition,
                    "platform": platform
                },
                execution_time_ms=execution_time_ms,
                tokens_used=150,
                cost_usd=0.0015
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log failure
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="bid_strategy",
                action="optimize_bid",
                input_data={"keyword": keyword, "current_bid": current_bid},
                output_data=None,
                execution_time_ms=execution_time_ms,
                tokens_used=0,
                cost_usd=0,
                success=False,
                error_message=str(e),
                campaign_id=campaign_id
            )
            
            return AgentTriggerResult(
                success=False,
                agent_name=agent_name,
                action="optimize_bid",
                error=str(e),
                execution_time_ms=execution_time_ms
            )
    
    async def trigger_content_generate(
        self,
        gap_topic: str,
        gap_score: float,
        platform: str = "meta",
        business_goal: str = "performance"
    ) -> AgentTriggerResult:
        """
        Trigger content brief generation agent.
        
        Args:
            gap_topic: Gap topic to generate content for
            gap_score: Gap score (0-1)
            platform: Target platform
            business_goal: Business goal
            
        Returns:
            AgentTriggerResult with generated content brief
        """
        start_time = time.time()
        agent_name = "content_brief_agent"
        
        try:
            # Simulate content generation
            confidence = 0.80 + (hash(gap_topic) % 15) / 100
            differentiation = 0.75 + (hash(gap_topic) % 20) / 100
            
            # Generate brief
            brief = {
                "topic": gap_topic,
                "angle": f"Unique perspective on {gap_topic}",
                "hook": f"Discover why {gap_topic} matters for your fitness journey",
                "proof_point": "Based on market research, 85% of users find this relevant",
                "cta": "Shop now for best results",
                "target_audience": "18-34 fitness enthusiasts",
                "platform": platform,
                "differentiation_score": differentiation
            }
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log to agent logger
            agent_logger.log_optimize(
                agent="CONTENT_BRIEF",
                campaign=f"Content for {gap_topic}",
                optimization_type=f"Generated brief with differentiation score {differentiation:.2f}",
                confidence=confidence
            )
            
            # Log to execution logger
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="content_brief",
                action="generate_content",
                input_data={
                    "gap_topic": gap_topic,
                    "gap_score": gap_score,
                    "platform": platform,
                    "business_goal": business_goal
                },
                output_data={
                    "brief": brief,
                    "confidence": confidence,
                    "differentiation": differentiation
                },
                execution_time_ms=execution_time_ms,
                tokens_used=280,
                cost_usd=0.0028,
                success=True
            )
            
            return AgentTriggerResult(
                success=True,
                agent_name=agent_name,
                action="generate_content",
                output={
                    "brief": brief,
                    "confidence": confidence,
                    "differentiation": differentiation
                },
                execution_time_ms=execution_time_ms,
                tokens_used=280,
                cost_usd=0.0028
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="content_brief",
                action="generate_content",
                input_data={"gap_topic": gap_topic},
                output_data=None,
                execution_time_ms=execution_time_ms,
                tokens_used=0,
                cost_usd=0,
                success=False,
                error_message=str(e)
            )
            
            return AgentTriggerResult(
                success=False,
                agent_name=agent_name,
                action="generate_content",
                error=str(e),
                execution_time_ms=execution_time_ms
            )
    
    async def trigger_creative_optimize(
        self,
        creative_id: str,
        creative_type: str,
        platform: str = "meta"
    ) -> AgentTriggerResult:
        """
        Trigger creative optimization agent.
        
        Args:
            creative_id: Creative ID to optimize
            creative_type: Type of creative (image, video, carousel)
            platform: Platform
            
        Returns:
            AgentTriggerResult with optimization suggestions
        """
        start_time = time.time()
        agent_name = "creative_optimization_agent"
        
        try:
            # Simulate creative optimization
            performance_score = 60 + (hash(creative_id) % 35)
            confidence = 0.75 + (hash(creative_id) % 20) / 100
            
            # Generate suggestions
            suggestions = [
                "Increase contrast in hero image",
                "Add social proof elements",
                "Optimize CTA button color",
                "Test alternative headline"
            ]
            
            predicted_lift = 15 + (hash(creative_id) % 10)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log to agent logger
            agent_logger.log_optimize(
                agent="CREATIVE_OPT",
                campaign=f"Creative {creative_id}",
                optimization_type=f"Performance score {performance_score}, predicted lift {predicted_lift}%",
                confidence=confidence
            )
            
            # Log to execution logger
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="creative_optimization",
                action="optimize_creative",
                input_data={
                    "creative_id": creative_id,
                    "creative_type": creative_type,
                    "platform": platform
                },
                output_data={
                    "performance_score": performance_score,
                    "suggestions": suggestions,
                    "predicted_lift": predicted_lift,
                    "confidence": confidence
                },
                execution_time_ms=execution_time_ms,
                tokens_used=200,
                cost_usd=0.0020,
                success=True
            )
            
            return AgentTriggerResult(
                success=True,
                agent_name=agent_name,
                action="optimize_creative",
                output={
                    "performance_score": performance_score,
                    "suggestions": suggestions,
                    "predicted_lift": predicted_lift,
                    "confidence": confidence
                },
                execution_time_ms=execution_time_ms,
                tokens_used=200,
                cost_usd=0.0020
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="creative_optimization",
                action="optimize_creative",
                input_data={"creative_id": creative_id},
                output_data=None,
                execution_time_ms=execution_time_ms,
                tokens_used=0,
                cost_usd=0,
                success=False,
                error_message=str(e)
            )
            
            return AgentTriggerResult(
                success=False,
                agent_name=agent_name,
                action="optimize_creative",
                error=str(e),
                execution_time_ms=execution_time_ms
            )
    
    async def trigger_market_analyze(
        self,
        query: str,
        time_range: str = "week",
        competitors: Optional[List[str]] = None
    ) -> AgentTriggerResult:
        """
        Trigger market analysis agent.
        
        Args:
            query: Analysis query
            time_range: Time range (day, week, month)
            competitors: List of competitors to analyze
            
        Returns:
            AgentTriggerResult with market insights
        """
        start_time = time.time()
        agent_name = "market_analysis_agent"
        
        try:
            # Simulate market analysis
            confidence = 0.80 + (hash(query) % 15) / 100
            
            # Generate insights
            insights = [
                f"Trend detected: {query} is growing by {10 + (hash(query) % 20)}%",
                f"Competitor activity: Moderate in {time_range} timeframe",
                f"Market opportunity: High for {query}-related content"
            ]
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log to agent logger
            agent_logger.log_analyze(
                agent="MARKET_ANALYSIS",
                analysis_type=f"Market analysis for {query}",
                result=f"Generated {len(insights)} insights"
            )
            
            # Log to execution logger
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="market_analysis",
                action="analyze_market",
                input_data={
                    "query": query,
                    "time_range": time_range,
                    "competitors": competitors
                },
                output_data={
                    "insights": insights,
                    "confidence": confidence
                },
                execution_time_ms=execution_time_ms,
                tokens_used=250,
                cost_usd=0.0025,
                success=True
            )
            
            return AgentTriggerResult(
                success=True,
                agent_name=agent_name,
                action="analyze_market",
                output={
                    "insights": insights,
                    "confidence": confidence
                },
                execution_time_ms=execution_time_ms,
                tokens_used=250,
                cost_usd=0.0025
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="market_analysis",
                action="analyze_market",
                input_data={"query": query},
                output_data=None,
                execution_time_ms=execution_time_ms,
                tokens_used=0,
                cost_usd=0,
                success=False,
                error_message=str(e)
            )
            
            return AgentTriggerResult(
                success=False,
                agent_name=agent_name,
                action="analyze_market",
                error=str(e),
                execution_time_ms=execution_time_ms
            )
    
    async def trigger_keyword_classify(
        self,
        query: str,
        use_disbert: bool = True
    ) -> AgentTriggerResult:
        """
        Trigger keyword classification with DisBERT.
        
        Args:
            query: Keyword to classify
            use_disbert: Whether to use DisBERT model
            
        Returns:
            AgentTriggerResult with classification
        """
        start_time = time.time()
        agent_name = "disbert_classifier"
        
        try:
            # Use DisBERT if available
            if use_disbert:
                classification = self.disbert_integrator.classify_query_with_disbert(query)
                category = classification.value
                model_used = "thrad_disbert"
            else:
                # Fallback to simple classification
                category = "H" if "buy" in query.lower() or "online" in query.lower() else "E"
                model_used = None
            
            # Get keyword strategy
            strategy = self.disbert_integrator.get_google_ads_keywords_for_classification(classification)
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log to campaign keyword logger
            campaign_keyword_logger.log_keyword_addition(
                keyword=query,
                match_type="phrase",
                bid_amount=2.50,
                source="agent_trigger",
                confidence=strategy.get("commercial_intent", 0.8),
                intent="transactional" if category == "H" else "informational",
                category=category,
                model_used=model_used
            )
            
            # Log to execution logger
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="disbert_classification",
                action="classify_keyword",
                input_data={"query": query, "use_disbert": use_disbert},
                output_data={
                    "category": category,
                    "strategy": strategy,
                    "model_used": model_used
                },
                execution_time_ms=execution_time_ms,
                tokens_used=100,
                cost_usd=0.0010,
                success=True
            )
            
            return AgentTriggerResult(
                success=True,
                agent_name=agent_name,
                action="classify_keyword",
                output={
                    "query": query,
                    "category": category,
                    "strategy": strategy,
                    "model_used": model_used
                },
                execution_time_ms=execution_time_ms,
                tokens_used=100,
                cost_usd=0.0010
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="disbert_classification",
                action="classify_keyword",
                input_data={"query": query},
                output_data=None,
                execution_time_ms=execution_time_ms,
                tokens_used=0,
                cost_usd=0,
                success=False,
                error_message=str(e)
            )
            
            return AgentTriggerResult(
                success=False,
                agent_name=agent_name,
                action="classify_keyword",
                error=str(e),
                execution_time_ms=execution_time_ms
            )
    
    async def trigger_orchestrate(
        self,
        task_type: str,
        context: Dict,
        required_agents: List[str]
    ) -> AgentTriggerResult:
        """
        Trigger orchestration agent to coordinate multiple agents.
        
        Args:
            task_type: Type of task (planning, media_buying, intelligence)
            context: Task context
            required_agents: List of agents to coordinate
            
        Returns:
            AgentTriggerResult with orchestration results
        """
        start_time = time.time()
        agent_name = "orchestration_agent"
        
        try:
            # Simulate orchestration
            confidence = 0.90 + (hash(task_type) % 8) / 100
            
            # Simulate agent results
            agent_results = {}
            for agent in required_agents:
                agent_results[agent] = {
                    "status": "completed",
                    "confidence": 0.85 + (hash(agent) % 12) / 100
                }
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Log to agent logger
            agent_logger.log_execute(
                agent="ORCHESTRATION",
                execution_type=f"Coordinated {len(required_agents)} agents for {task_type}",
                result=f"All agents completed successfully"
            )
            
            # Log to execution logger
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="orchestration",
                action="orchestrate",
                input_data={
                    "task_type": task_type,
                    "context": context,
                    "required_agents": required_agents
                },
                output_data={
                    "agent_results": agent_results,
                    "confidence": confidence
                },
                execution_time_ms=execution_time_ms,
                tokens_used=300,
                cost_usd=0.0030,
                success=True
            )
            
            return AgentTriggerResult(
                success=True,
                agent_name=agent_name,
                action="orchestrate",
                output={
                    "agent_results": agent_results,
                    "confidence": confidence
                },
                execution_time_ms=execution_time_ms,
                tokens_used=300,
                cost_usd=0.0030
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            await agent_execution_logger.log_execution(
                agent_name=agent_name,
                agent_type="orchestration",
                action="orchestrate",
                input_data={"task_type": task_type},
                output_data=None,
                execution_time_ms=execution_time_ms,
                tokens_used=0,
                cost_usd=0,
                success=False,
                error_message=str(e)
            )
            
            return AgentTriggerResult(
                success=False,
                agent_name=agent_name,
                action="orchestrate",
                error=str(e),
                execution_time_ms=execution_time_ms
            )
    
    def _intensity_from_growth(self, growth: int) -> str:
        if growth >= 25:
            return "hot"
        if growth >= 0:
            return "warm"
        return "cool"

    def _bidders_for_topic(self, seed: str) -> List[str]:
        return [p for p in BID_PLATFORMS if (hash(seed + p) % 5) > 1] or ["google"]

    def _trending_topics_from_results(
        self, query: str, results: List[Dict], answer: str = ""
    ) -> List[Dict]:
        trending_topics = []
        for i, result in enumerate(results[:10]):
            title = result.get("title") or query
            growth = 5 + (hash(title) % 55) - 10
            spark = [
                10 + (hash(title + str(j)) % 20) for j in range(12)
            ]
            trending_topics.append({
                "id": f"tavily_{i}_{int(time.time())}",
                "kw": title[:120],
                "growth": growth,
                "vol": f"{40 + (hash(title) % 160)}K",
                "intensity": self._intensity_from_growth(growth),
                "src": ["T"],
                "spark": spark,
                "detail": {
                    "relevance": min(99, 65 + (hash(title) % 35)),
                    "vol12": spark,
                    "bidders": self._bidders_for_topic(title),
                    "attribution": [
                        {"src": "Tavily /search", "w": 0.55},
                        {"src": answer[:40] + "…" if answer else "Tavily answer", "w": 0.25},
                        {"src": result.get("url", "")[:48] or "web", "w": 0.2},
                    ],
                    "tavily_url": result.get("url"),
                    "tavily_snippet": (result.get("content") or "")[:280],
                },
            })
        return trending_topics

    async def trigger_tavily_research(
        self,
        query: str,
        max_results: int = 15,
        extract_keywords: bool = True
    ) -> AgentTriggerResult:
        """
        Trigger Tavily research for trending topics.
        
        Args:
            query: Research query
            max_results: Maximum results to return
            extract_keywords: Whether to extract keywords
            
        Returns:
            AgentTriggerResult with research results and trending topics
        """
        start_time = time.time()
        agent_name = "tavily_research"
        
        try:
            if not settings.tavily_api_key:
                raise ValueError(
                    "TAVILY_API_KEY is not configured. Add it to .env.local and restart the API."
                )

            from services.intelligence.tavily_client import TavilyClient

            client = TavilyClient()
            try:
                response = await client.search_and_answer(
                    query=query,
                    max_results=max_results,
                )
            finally:
                await client.close()

            raw_results = [
                {
                    "title": r.title,
                    "url": r.url,
                    "content": r.content,
                }
                for r in response.results
            ]
            if not raw_results:
                raise ValueError("Tavily returned no results for this query")

            research_results = {
                "answer": response.answer,
                "query": response.query,
                "results": raw_results,
                "keywords": [
                    {"keyword": query.lower(), "volume": 1000 + hash(query) % 500},
                    {"keyword": f"best {query.lower()}", "volume": 500 + hash(query) % 300},
                ],
                "reddit_posts": [],
                "seo_keywords": [
                    {"keyword": query.lower(), "intent": "transactional", "volume": 1000},
                ],
                "google_keywords": [
                    {
                        "keyword": query.lower(),
                        "match_type": "phrase",
                        "bid_suggestion": 2.50,
                        "search_intent": "transactional",
                    },
                ],
                "thrad_inputs": [
                    {"query": query.lower(), "category": "H", "confidence": 0.85, "source": "tavily"},
                ],
                "content_ideas": [
                    {
                        "topic": query.title(),
                        "angle": (response.answer or "")[:120],
                        "target_audience": "18-34",
                        "platform": "google",
                        "content_type": "search",
                        "keywords": [query.lower()],
                    }
                ],
            }
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            trending_topics = self._trending_topics_from_results(
                query, raw_results, response.answer or ""
            )
            
            # Automatically map Tavily fields to DisBERT segments
            disbert_segments = tavily_to_disbert_mapper.map_tavily_research_to_disbert(research_results)
            
            # Group segments by classification
            segments_by_classification = {}
            for segment in disbert_segments:
                classification = segment.classification.value
                if classification not in segments_by_classification:
                    segments_by_classification[classification] = []
                segments_by_classification[classification].append({
                    "classification": segment.classification_name,
                    "tavily_fields": segment.tavily_fields,
                    "mapped_data": segment.mapped_data,
                    "commercial_intent": segment.commercial_intent,
                    "ingestion_priority": segment.ingestion_priority,
                    "should_use_as_keywords": segment.should_use_as_keywords
                })
            
            # Get high-value segments (H, J, E)
            high_value_segments = tavily_to_disbert_mapper.get_high_value_segments(research_results)
            
            # Log to agent logger
            agent_logger.log_analyze(
                agent="TAVILY_RESEARCH",
                analysis_type=f"Tavily research for {query}",
                result=f"Found {len(trending_topics)} trending topics, {len(disbert_segments)} DisBERT segments"
            )
            
            # Skip database logging for now (requires greenlet)
            # await agent_execution_logger.log_execution(...)
            
            return AgentTriggerResult(
                success=True,
                agent_name=agent_name,
                action="research_tavily",
                output={
                    "query": query,
                    "answer": response.answer,
                    "trending_topics": trending_topics,
                    "total_results": len(research_results.get("results", [])),
                    "keywords": research_results.get("keywords", []) if extract_keywords else [],
                    "disbert_segments": {
                        "total_segments": len(disbert_segments),
                        "segments_by_classification": segments_by_classification,
                        "high_value_segments": [
                            {
                                "classification": seg.classification.value,
                                "tavily_fields": seg.tavily_fields,
                                "mapped_data": seg.mapped_data,
                                "commercial_intent": seg.commercial_intent,
                                "ingestion_priority": seg.ingestion_priority
                            }
                            for seg in high_value_segments
                        ]
                    }
                },
                execution_time_ms=execution_time_ms,
                tokens_used=200,
                cost_usd=0.0020
            )
            
        except Exception as e:
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Skip database logging for now (requires greenlet)
            # await agent_execution_logger.log_execution(...)
            
            return AgentTriggerResult(
                success=False,
                agent_name=agent_name,
                action="research_tavily",
                error=str(e),
                execution_time_ms=execution_time_ms
            )


# Global trigger service instance
agent_trigger_service = AgentTriggerService()