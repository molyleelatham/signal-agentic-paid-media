"""
Creative Optimization Agent.

This agent uses LLM to analyze and optimize creative performance.
Integrates with Overmind for tracing and optimization.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

from shared.agents.overmind_integration import BaseAgent, OvermindTracer


@dataclass
class CreativeAnalysis:
    """Analysis of creative performance."""
    
    creative_id: str
    performance_score: float
    strengths: List[str]
    weaknesses: List[str]
    optimization_suggestions: List[str]
    predicted_lift: float
    confidence: float


@dataclass
class CreativeVariation:
    """Suggested creative variation."""
    
    base_creative_id: str
    variation_type: str  # headline, image, cta, etc.
    suggested_change: str
    reasoning: str
    expected_improvement: str


class CreativeOptimizationAgent(BaseAgent):
    """
    Creative Optimization Agent.
    
    This agent:
    - Analyzes creative performance data
    - Identifies strengths and weaknesses
    - Suggests specific optimizations
    - Generates creative variations for testing
    """
    
    def __init__(
        self,
        overmind_tracer: OvermindTracer = None,
        llm_client: Any = None
    ):
        """
        Initialize creative optimization agent.
        
        Args:
            overmind_tracer: Overmind tracer instance
            llm_client: LLM client for creative analysis
        """
        super().__init__(
            name="CreativeOptimizationAgent",
            overmind_tracer=overmind_tracer,
            llm_client=llm_client
        )
    
    async def analyze_creative(
        self,
        creative_data: Dict,
        performance_metrics: Dict,
        benchmark_data: Dict = None
    ) -> CreativeAnalysis:
        """
        Analyze creative performance and provide optimization recommendations.
        
        This is the main agent function - uses LLM to provide creative insights
        that go beyond simple performance metrics.
        
        Args:
            creative_data: Creative content and metadata
            performance_metrics: Performance data (CTR, conversion rate, etc.)
            benchmark_data: Benchmark performance for comparison
        
        Returns:
            Creative analysis with optimization suggestions
        """
        # Store context in memory
        self.memory.store("current_creative", creative_data)
        self.memory.store("performance_metrics", performance_metrics)
        self.memory.store("benchmark_data", benchmark_data or {})
        
        # Build prompt for LLM
        prompt = self._build_analysis_prompt(
            creative_data,
            performance_metrics,
            benchmark_data
        )
        
        # Call LLM for creative analysis (with Overmind tracing)
        response = await self.think(
            prompt=prompt,
            context={
                "creative_data": creative_data,
                "performance_metrics": performance_metrics
            }
        )
        
        # Parse LLM response into structured analysis
        analysis = self._parse_analysis_response(response, creative_data, performance_metrics)
        
        # Record analysis
        self.memory.record_decision(
            agent_name=self.name,
            decision=f"Analyzed creative {creative_data.get('id', 'unknown')}",
            reasoning=f"Performance score: {analysis.performance_score:.2f}, {len(analysis.optimization_suggestions)} optimizations suggested",
            context={"creative_id": creative_data.get("id"), "performance_score": analysis.performance_score}
        )
        
        return analysis
    
    def _build_analysis_prompt(
        self,
        creative_data: Dict,
        performance_metrics: Dict,
        benchmark_data: Dict
    ) -> str:
        """
        Build prompt for creative analysis.
        
        Args:
            creative_data: Creative data
            performance_metrics: Performance metrics
            benchmark_data: Benchmark data
        
        Returns:
            LLM prompt
        """
        creative_type = creative_data.get("type", "unknown")
        headline = creative_data.get("headline", "No headline")
        description = creative_data.get("description", "No description")
        visual_elements = creative_data.get("visual_elements", [])
        
        ctr = performance_metrics.get("ctr", 0)
        conversion_rate = performance_metrics.get("conversion_rate", 0)
        engagement_rate = performance_metrics.get("engagement_rate", 0)
        
        benchmark_section = ""
        if benchmark_data:
            benchmark_ctr = benchmark_data.get("ctr", 0)
            benchmark_conv = benchmark_data.get("conversion_rate", 0)
            benchmark_section = f"""
BENCHMARK PERFORMANCE:
- Benchmark CTR: {benchmark_ctr:.2%}
- Benchmark Conversion Rate: {benchmark_conv:.2%}
"""
        
        prompt = f"""You are an expert creative optimizer for digital advertising. Analyze this creative:

CREATIVE DETAILS:
- Type: {creative_type}
- Headline: {headline}
- Description: {description}
- Visual Elements: {', '.join(visual_elements) if visual_elements else 'None specified'}

PERFORMANCE METRICS:
- CTR: {ctr:.2%}
- Conversion Rate: {conversion_rate:.2%}
- Engagement Rate: {engagement_rate:.2%}
{benchmark_section}

Analyze and provide:
1. Performance score (0-1) considering metrics vs benchmarks
2. Strengths (what's working well)
3. Weaknesses (what needs improvement)
4. Specific optimization suggestions (headline, imagery, CTA, targeting, etc.)
5. Predicted lift from optimizations
6. Confidence in your analysis

Be specific and actionable in your suggestions."""
        
        return prompt
    
    def _parse_analysis_response(
        self,
        response: str,
        creative_data: Dict,
        performance_metrics: Dict
    ) -> CreativeAnalysis:
        """
        Parse LLM response into structured analysis.
        
        Args:
            response: LLM response text
            creative_data: Original creative data
            performance_metrics: Performance metrics
        
        Returns:
            Structured creative analysis
        """
        # In production, this would properly parse the LLM response
        # For now, generate analysis based on performance metrics
        
        ctr = performance_metrics.get("ctr", 0)
        conversion_rate = performance_metrics.get("conversion_rate", 0)
        
        # Simple scoring logic
        performance_score = min(1.0, (ctr * 10) + (conversion_rate * 5))
        
        # Generate insights based on performance
        strengths = []
        weaknesses = []
        optimization_suggestions = []
        
        if ctr > 0.02:
            strengths.append("Strong click-through rate indicates compelling headline")
        else:
            weaknesses.append("Below-average CTR suggests headline needs improvement")
            optimization_suggestions.append("Test different headline variations with stronger hooks")
        
        if conversion_rate > 0.01:
            strengths.append("Good conversion rate shows effective landing page alignment")
        else:
            weaknesses.append("Low conversion rate indicates messaging mismatch")
            optimization_suggestions.append("Improve alignment between ad creative and landing page")
        
        if not strengths:
            strengths.append("Creative has clear messaging structure")
        
        if not optimization_suggestions:
            optimization_suggestions.append("Consider A/B testing different visual elements")
        
        return CreativeAnalysis(
            creative_id=creative_data.get("id", "unknown"),
            performance_score=performance_score,
            strengths=strengths,
            weaknesses=weaknesses,
            optimization_suggestions=optimization_suggestions,
            predicted_lift=0.15,  # 15% predicted improvement
            confidence=0.80
        )
    
    async def generate_creative_variations(
        self,
        base_creative: Dict,
        optimization_goals: List[str],
        performance_data: Dict = None
    ) -> List[CreativeVariation]:
        """
        Generate creative variations for testing.
        
        Args:
            base_creative: Base creative to vary
            optimization_goals: Goals for optimization (CTR, conversion, etc.)
            performance_data: Performance data to inform variations
        
        Returns:
            List of suggested creative variations
        """
        prompt = f"""Generate creative variations for A/B testing:

BASE CREATIVE:
- Headline: {base_creative.get('headline', 'No headline')}
- Description: {base_creative.get('description', 'No description')}
- CTA: {base_creative.get('cta', 'No CTA')}

OPTIMIZATION GOALS: {', '.join(optimization_goals)}

PERFORMANCE CONTEXT:
{self._format_performance_context(performance_data)}

Generate 3-5 specific variations covering:
1. Headline variations (different hooks, urgency, social proof)
2. Visual suggestions (imagery, color, layout)
3. CTA alternatives (different wording, placement)
4. Description tweaks (length, focus, tone)

For each variation, specify:
- What element to change
- Suggested change
- Reasoning behind the change
- Expected improvement"""
        
        variations_response = await self.think(
            prompt=prompt,
            context={
                "base_creative": base_creative,
                "optimization_goals": optimization_goals
            }
        )
        
        # Parse variations (simplified for now)
        return [
            CreativeVariation(
                base_creative_id=base_creative.get("id", "unknown"),
                variation_type="headline",
                suggested_change="Add urgency element with limited-time offer",
                reasoning="Urgency typically increases CTR by 15-20%",
                expected_improvement="+15% CTR"
            ),
            CreativeVariation(
                base_creative_id=base_creative.get("id", "unknown"),
                variation_type="cta",
                suggested_change="Make CTA more specific and benefit-oriented",
                reasoning="Specific CTAs outperform generic ones",
                expected_improvement="+10% conversion rate"
            )
        ]
    
    def _format_performance_context(self, performance_data: Dict) -> str:
        """Format performance data for prompt."""
        if not performance_data:
            return "No performance data available"
        
        return str(performance_data)
    
    async def analyze_creative_fatigue(
        self,
        creative_performance_history: List[Dict],
        time_threshold_days: int = 14
    ) -> Dict:
        """
        Analyze creative fatigue and recommend rotation timing.
        
        Args:
            creative_performance_history: Historical performance data
            time_threshold_days: Days to consider for fatigue analysis
        
        Returns:
        Fatigue analysis with rotation recommendations
        """
        if len(creative_performance_history) < 7:
            return {
                "fatigue_detected": False,
                "reason": "Insufficient data for fatigue analysis",
                "recommendation": "Continue monitoring"
            }
        
        # Calculate performance trend
        recent_performance = creative_performance_history[-7:]
        older_performance = creative_performance_history[-14:-7]
        
        recent_avg_ctr = sum(p.get("ctr", 0) for p in recent_performance) / len(recent_performance)
        older_avg_ctr = sum(p.get("ctr", 0) for p in older_performance) / len(older_performance)
        
        performance_decline = (older_avg_ctr - recent_avg_ctr) / older_avg_ctr if older_avg_ctr > 0 else 0
        
        prompt = f"""Analyze creative fatigue:

PERFORMANCE TREND:
- CTR 7-14 days ago: {older_avg_ctr:.2%}
- CTR last 7 days: {recent_avg_ctr:.2%}
- Performance decline: {performance_decline:.1%}

HISTORICAL PERFORMANCE:
{self._format_performance_history(creative_performance_history)}

Determine:
1. Is creative fatigue present? (yes/no)
2. Severity of fatigue (none/mild/moderate/severe)
3. Recommended action (continue/rotate/pause)
4. Optimal timing for rotation
5. Suggested rotation strategy"""
        
        fatigue_analysis = await self.think(
            prompt=prompt,
            context={
                "performance_history": creative_performance_history,
                "performance_decline": performance_decline
            }
        )
        
        # Simple fatigue detection logic
        fatigue_detected = performance_decline > 0.15  # 15% decline threshold
        
        return {
            "fatigue_detected": fatigue_detected,
            "performance_decline": performance_decline,
            "severity": "moderate" if performance_decline > 0.15 else "mild" if performance_decline > 0.05 else "none",
            "recommendation": "Rotate creative within 3-5 days" if fatigue_detected else "Continue current creative",
            "analysis": fatigue_analysis,
            "confidence": 0.75
        }
    
    def _format_performance_history(self, performance_history: List[Dict]) -> str:
        """Format performance history for prompt."""
        if not performance_history:
            return "No performance history available"
        
        return f"Analysis of {len(performance_history)} data points over time"