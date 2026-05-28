"""
Agent Trigger Service

Provides unified interface for triggering all agents with proper logging.
"""

import asyncio
import uuid
import time
from dataclasses import asdict
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

    def _bidders_for_topic(
        self, result: Dict, google_keywords: List[Dict]
    ) -> List[str]:
        """Infer active bidders from Tavily result URL and research keywords."""
        bidders: List[str] = []
        url = (result.get("url") or "").lower()
        if google_keywords:
            bidders.append("google")
        if "tiktok.com" in url:
            bidders.append("tiktok")
        if "bing.com" in url or "microsoft" in url:
            bidders.append("msft")
        for kw in google_keywords:
            comp = (kw.get("competition") or "").lower()
            if comp in ("high", "medium") and "google" not in bidders:
                bidders.append("google")
        return bidders or list(BID_PLATFORMS[:1])

    def _intent_from_thrad_category(self, category: str) -> str:
        """Map Thrad pipeline category letter to audience intent label."""
        letter = str(category or "E")[:1].upper()
        return {
            "H": "PURCHASE",
            "G": "COMPARISON",
            "A": "DISCOVERY",
            "J": "LOYALTY",
            "E": "DISCOVERY",
        }.get(letter, "DISCOVERY")

    def _classify_thrad_category_from_text(self, text: str) -> str:
        """Lightweight H/G/E/J classifier for fallback inputs."""
        lower = text.lower()
        if any(w in lower for w in ("buy", "price", "best", "vs", "compare", "worth")):
            return "H" if "buy" in lower or "price" in lower else "G"
        if any(w in lower for w in ("how", "why", "guide", "tips")):
            return "E"
        return "E"

    def _extract_query_terms(self, text: str, limit: int = 4) -> List[str]:
        import re

        words = re.findall(r"\b[a-zA-Z]{4,}\b", (text or "").lower())
        stop = {
            "that", "this", "with", "from", "your", "have", "what", "when",
            "where", "which", "about", "their", "there", "would", "could",
        }
        out: List[str] = []
        for w in words:
            if w not in stop and w not in out:
                out.append(w)
            if len(out) >= limit:
                break
        return out

    def _ensure_thrad_inputs(self, query: str, research_results: Dict) -> List[Dict]:
        """Guarantee thrad_inputs exist by mining Tavily + research payloads."""
        existing = list(research_results.get("thrad_inputs") or [])
        seen = {(x.get("query") or "").lower() for x in existing if x.get("query")}
        out = list(existing)

        def add(inp: Dict) -> None:
            q = (inp.get("query") or "").strip().lower()
            if not q or q in seen:
                return
            seen.add(q)
            out.append(inp)

        for post in research_results.get("reddit_posts", [])[:8]:
            title = (post.get("title") or "").strip()
            if not title:
                continue
            for kw in (post.get("keywords") or [])[:2]:
                add({
                    "query": kw,
                    "category": self._classify_thrad_category_from_text(title),
                    "confidence": float(post.get("relevance_score", 0.6)),
                    "source": "reddit",
                    "context": title[:160],
                })
            add({
                "query": title[:80],
                "category": self._classify_thrad_category_from_text(title),
                "confidence": float(post.get("relevance_score", 0.65)),
                "source": "reddit",
                "context": (post.get("content") or "")[:160],
            })

        for kw in research_results.get("google_keywords", [])[:10]:
            keyword = (kw.get("keyword") or "").strip()
            if keyword:
                add({
                    "query": keyword,
                    "category": "H" if kw.get("search_intent") == "transactional" else "G",
                    "confidence": float(kw.get("relevance_to_gymshark", 0.7)),
                    "source": "google_keywords",
                    "context": f"Google Ads · {kw.get('match_type', 'phrase')} match",
                })

        for seo in research_results.get("seo_keywords", [])[:8]:
            keyword = (seo.get("keyword") or "").strip()
            if keyword:
                add({
                    "query": keyword,
                    "category": "E" if seo.get("intent") == "informational" else "H",
                    "confidence": float(seo.get("confidence", 0.6)),
                    "source": "seo",
                    "context": f"SEO · {seo.get('source', 'research')}",
                })

        for idea in research_results.get("content_ideas", [])[:5]:
            topic = (idea.get("topic") or "").strip()
            angle = (idea.get("angle") or "").strip()
            if topic or angle:
                add({
                    "query": topic or angle,
                    "category": "G",
                    "confidence": float(idea.get("opportunity_score", 0.65)),
                    "source": "content_ideas",
                    "context": angle[:160] if angle else topic[:160],
                })

        for r in research_results.get("results", [])[:10]:
            title = (r.get("title") or "").strip()
            content = (r.get("content") or "")[:300]
            if not title:
                continue
            score = float(r.get("score", 0.5))
            for term in self._extract_query_terms(f"{title} {content}", 3):
                add({
                    "query": term,
                    "category": self._classify_thrad_category_from_text(title),
                    "confidence": min(0.95, score + 0.15),
                    "source": "tavily",
                    "context": title[:160],
                })
            add({
                "query": title[:90],
                "category": self._classify_thrad_category_from_text(title + content),
                "confidence": min(0.95, score + 0.2),
                "source": "tavily",
                "context": content[:160],
            })

        if len(out) < 3 and query:
            add({
                "query": query,
                "category": "H",
                "confidence": 0.75,
                "source": "tavily",
                "context": (research_results.get("answer") or "")[:160],
            })

        research_results["thrad_inputs"] = out
        return out

    def _audience_item_from_payload(
        self,
        display_q: str,
        classify_text: str,
        source: str,
        confidence: float,
        thrad_cat: str,
    ) -> Dict:
        """Build one Section B row with DisBERT classification."""
        classification = self.disbert_integrator.classify_query_with_disbert(classify_text)
        strategy = self.disbert_integrator.get_google_ads_keywords_for_classification(
            classification
        )
        commercial = float(strategy.commercial_intent) if strategy else 0.5
        ingestion = self.disbert_integrator.get_ingestion_rule_for_classification(
            classification
        )
        ingest_priority = float(ingestion.ingestion_priority) if ingestion else 5.0
        intent = self._intent_from_thrad_category(thrad_cat)
        if commercial >= 0.8:
            intent = "PURCHASE"
        elif commercial >= 0.65:
            intent = "COMPARISON"

        return {
            "q": display_q[:140],
            "intent": intent,
            "vol": round(confidence * 10, 1),
            "trend": "up" if confidence >= 0.55 else "flat",
            "adRank": round(4 + commercial * 5, 1),
            "ctxScore": int(min(99, 40 + ingest_priority * 5 + confidence * 20)),
            "source": source,
            "thrad_category": thrad_cat,
            "disbert_classification": (
                strategy.classification_name
                if strategy
                else classification.name.lower()
            ),
            "commercial_intent": round(commercial, 2),
        }

    def _audience_queries_from_research(
        self, query: str, research_results: Dict, answer: str
    ) -> List[Dict]:
        """Section B: fill from Thrad inputs + Reddit, SEO, Google, Tavily research."""
        self._ensure_thrad_inputs(query, research_results)
        thrad_inputs = research_results.get("thrad_inputs") or []

        queries: List[Dict] = []
        seen: set = set()

        def push(item: Dict) -> None:
            key = (item.get("q") or "").lower().strip()
            if not key or key in seen:
                return
            seen.add(key)
            queries.append(item)

        for ti in sorted(
            thrad_inputs,
            key=lambda x: float(x.get("confidence", 0)),
            reverse=True,
        ):
            raw_query = (ti.get("query") or "").strip()
            context = (ti.get("context") or "").strip()
            if not raw_query and not context:
                continue
            if context and (len(raw_query) < 24 or " " not in raw_query):
                display_q = context[:140]
            else:
                display_q = raw_query[:140]
            classify_text = raw_query if len(raw_query) > 8 else f"{raw_query} {context}".strip()
            push(
                self._audience_item_from_payload(
                    display_q=display_q,
                    classify_text=classify_text,
                    source=ti.get("source", "thrad"),
                    confidence=float(ti.get("confidence", 0.7)),
                    thrad_cat=str(ti.get("category", "E"))[:1].upper(),
                )
            )

        if answer and len(queries) < 12:
            for sentence in [s.strip() for s in answer.replace("?", "?\n").split("\n") if s.strip()][:3]:
                if len(sentence) < 20:
                    continue
                push(
                    self._audience_item_from_payload(
                        display_q=sentence[:140],
                        classify_text=sentence,
                        source="tavily_answer",
                        confidence=0.78,
                        thrad_cat="E",
                    )
                )

        return queries[:12]

    def _trace_lines_from_research(
        self,
        query: str,
        answer: str,
        raw_results: List[Dict],
        trending_topics: List[Dict],
        disbert_segments: List,
        high_value_segments: List,
        execution_time_ms: int,
        audience_query_count: int = 0,
    ) -> List[Dict]:
        """Plain-English lines for Overmind trace terminal."""
        lines = [
            {"msg": f'Scanning Tavily for "{query}"…', "tone": "work"},
            {
                "msg": f"Received {len(raw_results)} sources in {execution_time_ms}ms.",
                "tone": "ok",
            },
        ]
        if answer:
            lines.append({"msg": answer[:220], "tone": "info"})
        for t in trending_topics[:8]:
            lines.append({
                "msg": f"Topic indexed: {t.get('kw', '')[:72]} ({t.get('growth', 0):+}%)",
                "tone": "ok" if t.get("growth", 0) >= 15 else "info",
            })
        if audience_query_count:
            lines.append({
                "msg": f"Section B: {audience_query_count} Thrad inputs · DisBERT classified.",
                "tone": "ok",
            })
        if disbert_segments:
            lines.append({
                "msg": f"DisBERT mapped {len(disbert_segments)} segments from Tavily fields.",
                "tone": "ok",
            })
        for seg in high_value_segments[:5]:
            lines.append({
                "msg": f"High-value {seg.classification.value}: {', '.join(seg.tavily_fields)}",
                "tone": "info",
            })
        return lines

    def _trending_topics_from_results(
        self,
        query: str,
        results: List[Dict],
        answer: str = "",
        google_keywords: Optional[List[Dict]] = None,
    ) -> List[Dict]:
        trending_topics = []
        google_keywords = google_keywords or []
        for i, result in enumerate(results[:10]):
            title = result.get("title") or query
            score = float(result.get("score") or 0.5)
            growth = int(round((score - 0.45) * 80))
            relevance = min(99, max(1, int(score * 100)))
            base = max(8, int(score * 40))
            spark = [base + int(score * 6 * (j / 11)) for j in range(12)]
            vol_k = max(1, int(score * 220))
            trending_topics.append({
                "id": f"tavily_{i}_{int(time.time())}",
                "kw": title[:120],
                "growth": growth,
                "vol": f"{vol_k}K",
                "intensity": self._intensity_from_growth(growth),
                "src": ["T"],
                "spark": spark,
                "detail": {
                    "relevance": relevance,
                    "vol12": spark,
                    "bidders": self._bidders_for_topic(result, google_keywords),
                    "attribution": [
                        {"src": "Tavily /search", "w": round(score, 2)},
                        {
                            "src": (answer[:48] + "…") if answer and len(answer) > 48 else (answer or "Tavily answer"),
                            "w": round(max(0.1, 1.0 - score) * 0.5, 2),
                        },
                        {
                            "src": result.get("url", "")[:56] or "source",
                            "w": round(0.15 + (1 - score) * 0.2, 2),
                        },
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
                    "score": r.score,
                }
                for r in response.results
            ]
            if not raw_results:
                raise ValueError("Tavily returned no results for this query")

            from services.intelligence.tavily_research import GymsharkTavilyResearch

            research_service = GymsharkTavilyResearch(tavily_api_key=settings.tavily_api_key)
            comprehensive = await asyncio.to_thread(
                research_service.perform_comprehensive_research,
                base_query=query,
                max_results_per_source=min(max_results, 10),
                time_range="month",
            )

            google_keywords = [asdict(kw) for kw in comprehensive.google_keywords]
            seo_keywords = [
                {
                    "keyword": kw.keyword,
                    "intent": kw.intent,
                    "volume": kw.search_volume,
                    "confidence": kw.confidence,
                    "source": kw.source,
                }
                for kw in comprehensive.seo_keywords
            ]
            thrad_inputs = [
                {
                    "query": inp.query,
                    "category": inp.category,
                    "confidence": inp.confidence,
                    "source": inp.source,
                    "context": inp.context,
                }
                for inp in comprehensive.thrad_inputs
            ]
            keywords = [
                {"keyword": kw.get("keyword", ""), "volume": kw.get("bid_suggestion")}
                for kw in google_keywords
                if kw.get("keyword")
            ]
            for seo in seo_keywords:
                if seo.get("keyword"):
                    keywords.append({
                        "keyword": seo["keyword"],
                        "volume": seo.get("volume"),
                    })

            research_results = {
                "answer": response.answer or comprehensive.summary,
                "query": response.query,
                "results": raw_results,
                "keywords": keywords,
                "reddit_posts": [asdict(p) for p in comprehensive.reddit_posts],
                "seo_keywords": seo_keywords,
                "google_keywords": google_keywords,
                "thrad_inputs": thrad_inputs,
                "content_ideas": [asdict(idea) for idea in comprehensive.content_ideas],
            }
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            trending_topics = self._trending_topics_from_results(
                query,
                raw_results,
                response.answer or "",
                google_keywords=google_keywords,
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
            
            audience_queries = self._audience_queries_from_research(
                query, research_results, response.answer or ""
            )
            if audience_queries:
                agent_logger.log_analyze(
                    agent="THRAD_BERT",
                    analysis_type="Section B audience queries",
                    result=f"{len(audience_queries)} DisBERT-classified Thrad inputs",
                )
            trace_lines = self._trace_lines_from_research(
                query,
                response.answer or "",
                raw_results,
                trending_topics,
                disbert_segments,
                high_value_segments,
                execution_time_ms,
                audience_query_count=len(audience_queries),
            )

            agent_logger.log_analyze(
                agent="TAVILY_RESEARCH",
                analysis_type=f"Tavily research for {query}",
                result=f"Found {len(trending_topics)} topics, {len(audience_queries)} AI queries",
            )
            for t in trending_topics[:5]:
                agent_logger.log_monitor(
                    agent="TAVILY_RESEARCH",
                    metric=t.get("kw", "topic")[:48],
                    value=f"+{t.get('growth', 0)}% relevance {t.get('detail', {}).get('relevance', 0)}",
                )
            
            return AgentTriggerResult(
                success=True,
                agent_name=agent_name,
                action="research_tavily",
                output={
                    "query": query,
                    "answer": response.answer,
                    "trending_topics": trending_topics,
                    "audience_queries": audience_queries,
                    "thrad_inputs": research_results.get("thrad_inputs", []),
                    "trace_lines": trace_lines,
                    "agent_logs": agent_logger.get_logs_dict(25),
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