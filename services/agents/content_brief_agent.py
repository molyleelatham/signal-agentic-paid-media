"""
Content Brief Generation Agent.

This agent uses LLM to generate creative briefs based on gap analysis.
Integrates with Overmind for tracing and optimization.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

from shared.agents.overmind_integration import BaseAgent, OvermindTracer
from shared.agents.cursor_integration import CursorComposerService


@dataclass
class ContentBrief:
    """Generated content brief."""
    
    topic: str
    angle: str
    hook: str
    proof_point: str
    cta: str
    target_audience: str
    platform: str
    reasoning: str
    confidence: float
    differentiation_score: float


class ContentBriefAgent(BaseAgent):
    """
    Content Brief Generation Agent.
    
    This agent:
    - Analyzes gap matrix results to identify opportunities
    - Generates creative briefs for high-priority gaps
    - Ensures differentiation from competitor angles
    - Tailors content to specific platforms and goals
    """
    
    def __init__(
        self,
        overmind_tracer: OvermindTracer = None,
        llm_client: Any = None,
        cursor_composer: CursorComposerService = None,
    ):
        """
        Initialize content brief agent.
        
        Args:
            overmind_tracer: Overmind tracer instance
            llm_client: LLM client for content generation
            cursor_composer: Cursor Composer 2.5 service
        """
        super().__init__(
            name="ContentBriefAgent",
            overmind_tracer=overmind_tracer,
            llm_client=llm_client,
            cursor_composer=cursor_composer,
        )
    
    async def generate_brief(
        self,
        gap_topic: Dict,
        platform: str,
        goal_type: str,
        competitor_angles: List[str] = None
    ) -> ContentBrief:
        """
        Generate a creative brief for a gap topic.
        
        This is the main agent function - uses LLM to create strategic content briefs.
        
        Args:
            gap_topic: Gap topic data from BERTopic analysis
            platform: Target platform (meta, google, thrad)
            goal_type: Campaign goal (lead_generation, brand_awareness, etc.)
            competitor_angles: Known competitor angles to differentiate from
        
        Returns:
            Generated content brief
        """
        # Store context in memory
        self.memory.store("current_gap", gap_topic)
        self.memory.store("target_platform", platform)
        self.memory.store("campaign_goal", goal_type)
        self.memory.store("competitor_angles", competitor_angles or [])
        
        # Build prompt for LLM
        prompt = self._build_brief_generation_prompt(
            gap_topic,
            platform,
            goal_type,
            competitor_angles
        )
        
        # Call LLM (with Overmind tracing in production)
        response = await self.think(
            prompt=prompt,
            context={
                "gap_topic": gap_topic,
                "platform": platform,
                "goal": goal_type
            }
        )
        
        # Parse LLM response into structured brief
        brief = self._parse_brief_response(response, gap_topic, platform, goal_type)
        
        # Record decision
        self.memory.record_decision(
            agent_name=self.name,
            decision=f"Generated brief for topic: {brief.topic}",
            reasoning=brief.reasoning,
            context={
                "gap_topic": gap_topic,
                "platform": platform,
                "goal": goal_type
            }
        )
        
        return brief
    
    def _build_brief_generation_prompt(
        self,
        gap_topic: Dict,
        platform: str,
        goal_type: str,
        competitor_angles: List[str]
    ) -> str:
        """
        Build prompt for content brief generation.
        
        Args:
            gap_topic: Gap topic data
            platform: Target platform
            goal_type: Campaign goal
            competitor_angles: Competitor content angles
        
        Returns:
            LLM prompt
        """
        topic_name = gap_topic.get("name", "Unknown topic")
        zone = gap_topic.get("zone", "unknown")
        intent_score = gap_topic.get("intent_score", 0)
        
        competitor_section = ""
        if competitor_angles:
            competitor_section = f"\nCompetitor angles to avoid:\n" + "\n".join([f"- {angle}" for angle in competitor_angles])
        
        prompt = f"""You are an expert content strategist for media buying. Generate a creative brief for the following opportunity:

TOPIC: {topic_name}
ZONE: {zone} (high intent opportunity)
INTENT SCORE: {intent_score:.2f}
PLATFORM: {platform}
CAMPAIGN GOAL: {goal_type}

{competitor_section}

Generate a content brief with:
1. Strategic angle (differentiated from competitors)
2. Compelling hook (appropriate for the platform)
3. Specific proof point (verifiable, not generic)
4. Clear CTA (matching the intent stage)
5. Target audience description

Ensure the brief is specific enough that a creative could execute without clarifying questions."""
        
        return prompt
    
    def _parse_brief_response(
        self,
        response: str,
        gap_topic: Dict,
        platform: str,
        goal_type: str
    ) -> ContentBrief:
        """
        Parse LLM response into structured brief.
        
        Args:
            response: LLM response text
            gap_topic: Original gap topic
            platform: Target platform
            goal_type: Campaign goal
        
        Returns:
            Structured content brief
        """
        # In production, this would properly parse the LLM response
        # For now, create a structured brief from the response
        
        return ContentBrief(
            topic=gap_topic.get("name", "Unknown topic"),
            angle=response[:200],  # First part as angle
            hook="Attention-grabbing hook based on gap analysis",
            proof_point="Data-driven proof point from market intelligence",
            cta="Clear call-to-action aligned with campaign goal",
            target_audience=self._infer_target_audience(goal_type),
            platform=platform,
            reasoning=f"Generated based on gap zone {gap_topic.get('zone')} with intent score {gap_topic.get('intent_score', 0):.2f}",
            confidence=0.85,
            differentiation_score=0.78
        )
    
    def _infer_target_audience(self, goal_type: str) -> str:
        """Infer target audience from goal type."""
        audience_mapping = {
            "lead_generation": "Prospects showing high purchase intent",
            "customer_acquisition": "Ready-to-buy prospects",
            "brand_awareness": "Broad audience in discovery phase",
            "retargeting": "Previously engaged warm prospects"
        }
        return audience_mapping.get(goal_type, "General audience")
    
    async def evaluate_brief_quality(
        self,
        brief: ContentBrief,
        gap_topic: Dict
    ) -> Dict:
        """
        Evaluate the quality of a generated brief.
        
        Args:
            brief: Generated content brief
            gap_topic: Original gap topic
        
        Returns:
            Quality evaluation with scores
        """
        # Quality criteria from Module 10.2
        criteria = [
            "Strategic angle is differentiated from competitor angles",
            "Hook type is appropriate for the specified platform",
            "Proof point is specific and verifiable",
            "CTA matches the intent stage of the target audience",
            "Brief contains enough specificity for execution"
        ]
        
        # Use LLM to evaluate against criteria (with Overmind tracing)
        evaluation_prompt = f"""Evaluate this content brief against the following quality criteria:

BRIEF:
Topic: {brief.topic}
Angle: {brief.angle}
Hook: {brief.hook}
Proof Point: {brief.proof_point}
CTA: {brief.cta}

CRITERIA:
{chr(10).join([f"{i+1}. {criterion}" for i, criterion in enumerate(criteria)])}

Score each criterion from 0-1 and provide overall assessment."""
        
        evaluation = await self.think(
            prompt=evaluation_prompt,
            context={"brief": brief, "criteria": criteria}
        )
        
        return {
            "criteria_scores": {criterion: 0.8 for criterion in criteria},  # Placeholder
            "overall_score": brief.confidence,
            "evaluation_text": evaluation,
            "passed_threshold": brief.confidence > 0.7
        }
    
    async def generate_multiple_briefs(
        self,
        gap_topics: List[Dict],
        platform: str,
        goal_type: str,
        max_briefs: int = 5
    ) -> List[ContentBrief]:
        """
        Generate briefs for multiple gap topics.
        
        Args:
            gap_topics: List of gap topics
            platform: Target platform
            goal_type: Campaign goal
            max_briefs: Maximum number of briefs to generate
        
        Returns:
            List of generated content briefs
        """
        briefs = []
        
        # Prioritize by intent score
        sorted_topics = sorted(gap_topics, key=lambda x: x.get("intent_score", 0), reverse=True)
        
        for topic in sorted_topics[:max_briefs]:
            try:
                brief = await self.generate_brief(
                    gap_topic=topic,
                    platform=platform,
                    goal_type=goal_type
                )
                briefs.append(brief)
            except Exception as e:
                print(f"Error generating brief for topic {topic.get('name')}: {e}")
                continue
        
        return briefs
    
    def get_performance_feedback(self, brief_id: str, performance_metrics: Dict) -> None:
        """
        Receive performance feedback for a brief to improve future generation.
        
        Args:
            brief_id: Identifier for the brief
            performance_metrics: Performance data (CTR, conversions, etc.)
        """
        # Store in long-term memory for learning
        self.memory.store(
            f"brief_performance_{brief_id}",
            performance_metrics,
            memory_type="long"
        )
        
        # This would trigger Overmind optimization in production
        if self.overmind_tracer.client:
            self.overmind_tracer.log_outcome(
                trace_id=brief_id,
                outcome_label="performance_score",
                outcome_value=performance_metrics.get("score", 0)
            )