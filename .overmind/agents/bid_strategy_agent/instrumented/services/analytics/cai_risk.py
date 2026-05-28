"""
Goal-Adjusted Concentration Risk (CAI) Monitor.

This implements Module 9 from the technical spec:
- Creative Attention Index (CAI) calculation
- Goal-conditional target assessment
- Risk scoring and flagging
"""
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CAIResult:
    """Result of CAI calculation."""
    
    actual_cai: float
    target_cai: float
    deviation: float
    risk_score: float
    flag: bool
    direction: str  # "too_concentrated" or "too_dispersed"


class CAIRiskMonitor:
    """
    Goal-Adjusted Concentration Risk (CAI) Monitor implementation.
    
    This implements Module 9 from the technical spec:
    - CAI measures how evenly impressions are distributed
    - CAI is not universally good or bad
    - Risk is deviation from optimal concentration for campaign goal
    """
    
    # Goal concentration targets from Module 9.2
    GOAL_CONCENTRATION_TARGETS = {
        "lead_generation": {
            "target_cai": 0.55,
            "tolerance": 0.15
        },
        "customer_acquisition": {
            "target_cai": 0.40,
            "tolerance": 0.15
        },
        "brand_awareness": {
            "target_cai": 0.20,
            "tolerance": 0.10
        },
        "retargeting": {
            "target_cai": 0.80,
            "tolerance": 0.10
        }
    }
    
    def compute_cai(self, impression_shares: Dict[str, float]) -> float:
        """
        Compute Creative Attention Index (CAI).
        
        CAI is a Herfindahl-Hirschman style concentration measure.
        - 0 = perfectly distributed (one cluster per impression)
        - 1 = all impressions on one cluster
        
        Args:
            impression_shares: Dict mapping cluster_id to fraction_of_total_impressions
        
        Returns:
            CAI value in [0, 1]
        """
        if not impression_shares:
            return 0.0
        
        # Normalize shares to ensure they sum to 1
        total = sum(impression_shares.values())
        if total == 0:
            return 0.0
        
        normalized_shares = {k: v / total for k, v in impression_shares.items()}
        
        # Calculate Herfindahl-Hirschman Index
        cai = sum(share ** 2 for share in normalized_shares.values())
        
        return float(cai)
    
    def goal_adjusted_risk(
        self,
        actual_cai: float,
        goal_type: str
    ) -> CAIResult:
        """
        Calculate goal-adjusted risk score.
        
        Args:
            actual_cai: Actual CAI value
            goal_type: Campaign goal type
        
        Returns:
            CAIResult with risk assessment
        """
        if goal_type not in self.GOAL_CONCENTRATION_TARGETS:
            raise ValueError(f"Unknown goal type: {goal_type}")
        
        target = self.GOAL_CONCENTRATION_TARGETS[goal_type]
        target_cai = target["target_cai"]
        tolerance = target["tolerance"]
        
        # Calculate deviation from target
        deviation = abs(actual_cai - target_cai)
        
        # Risk score: deviation beyond tolerance
        risk_score = max(0.0, deviation - tolerance)
        
        # Flag if risk score is significant
        flag = risk_score > 0.1
        
        # Determine direction
        direction = "too_concentrated" if actual_cai > target_cai else "too_dispersed"
        
        return CAIResult(
            actual_cai=float(actual_cai),
            target_cai=float(target_cai),
            deviation=float(deviation),
            risk_score=float(risk_score),
            flag=flag,
            direction=direction
        )
    
    def get_goal_targets(self, goal_type: str) -> Dict[str, float]:
        """
        Get concentration targets for a goal type.
        
        Args:
            goal_type: Campaign goal type
        
        Returns:
            Dict with target_cai and tolerance
        """
        if goal_type not in self.GOAL_CONCENTRATION_TARGETS:
            raise ValueError(f"Unknown goal type: {goal_type}")
        
        return self.GOAL_CONCENTRATION_TARGETS[goal_type].copy()
    
    def validate_goal_type(self, goal_type: str) -> bool:
        """
        Validate that a goal type is supported.
        
        Args:
            goal_type: Goal type to validate
        
        Returns:
            True if valid, False otherwise
        """
        return goal_type in self.GOAL_CONCENTRATION_TARGETS
    
    def get_risk_explanation(
        self,
        cai_result: CAIResult,
        goal_type: str
    ) -> str:
        """
        Get human-readable risk explanation.
        
        Args:
            cai_result: CAI calculation result
            goal_type: Campaign goal type
        
        Returns:
            Human-readable explanation
        """
        if not cai_result.flag:
            return f"CAI is within optimal range for {goal_type}."
        
        target = self.GOAL_CONCENTRATION_TARGETS[goal_type]
        target_cai = target["target_cai"]
        
        if cai_result.direction == "too_concentrated":
            return (
                f"CAI is {cai_result.actual_cai:.2f}, which is above the target of {target_cai:.2f} "
                f"for {goal_type}. Your impressions are too concentrated in few segments. "
                f"Consider diversifying your audience targeting."
            )
        else:
            return (
                f"CAI is {cai_result.actual_cai:.2f}, which is below the target of {target_cai:.2f} "
                f"for {goal_type}. Your impressions are too dispersed. "
                f"Consider focusing on high-performing segments."
            )


class PortfolioRiskManager:
    """
    High-level portfolio risk management using CAI.
    
    Monitors concentration risk across multiple campaigns and provides recommendations.
    """
    
    def __init__(self, cai_monitor: CAIRiskMonitor = None):
        """
        Initialize portfolio risk manager.
        
        Args:
            cai_monitor: CAI risk monitor instance
        """
        self.cai_monitor = cai_monitor or CAIRiskMonitor()
        
        # Track impression data by campaign
        self.campaign_impressions: Dict[str, Dict[str, int]] = {}
    
    def add_campaign_impressions(
        self,
        campaign_id: str,
        cluster_impressions: Dict[str, int]
    ) -> None:
        """
        Add impression data for a campaign.
        
        Args:
            campaign_id: Campaign identifier
            cluster_impressions: Dict mapping cluster_id to impression count
        """
        self.campaign_impressions[campaign_id] = cluster_impressions
    
    def assess_campaign_risk(
        self,
        campaign_id: str,
        goal_type: str
    ) -> CAIResult:
        """
        Assess concentration risk for a campaign.
        
        Args:
            campaign_id: Campaign identifier
            goal_type: Campaign goal type
        
        Returns:
            CAIResult with risk assessment
        """
        if campaign_id not in self.campaign_impressions:
            raise ValueError(f"No impression data for campaign: {campaign_id}")
        
        cluster_impressions = self.campaign_impressions[campaign_id]
        
        # Calculate impression shares
        total_impressions = sum(cluster_impressions.values())
        if total_impressions == 0:
            impression_shares = {}
        else:
            impression_shares = {
                cluster_id: count / total_impressions
                for cluster_id, count in cluster_impressions.items()
            }
        
        # Compute CAI
        actual_cai = self.cai_monitor.compute_cai(impression_shares)
        
        # Calculate goal-adjusted risk
        return self.cai_monitor.goal_adjusted_risk(actual_cai, goal_type)
    
    def assess_portfolio_risk(
        self,
        campaign_goals: Dict[str, str]
    ) -> Dict[str, CAIResult]:
        """
        Assess risk across all campaigns.
        
        Args:
            campaign_goals: Dict mapping campaign_id to goal_type
        
        Returns:
            Dict mapping campaign_id to CAIResult
        """
        results = {}
        
        for campaign_id, goal_type in campaign_goals.items():
            try:
                result = self.assess_campaign_risk(campaign_id, goal_type)
                results[campaign_id] = result
            except ValueError as e:
                print(f"Error assessing campaign {campaign_id}: {e}")
                results[campaign_id] = None
        
        return results
    
    def get_risk_summary(self, campaign_goals: Dict[str, str]) -> Dict:
        """
        Get summary of portfolio risk.
        
        Args:
            campaign_goals: Dict mapping campaign_id to goal_type
        
        Returns:
            Dict with risk summary statistics
        """
        results = self.assess_portfolio_risk(campaign_goals)
        
        flagged_campaigns = [
            campaign_id for campaign_id, result in results.items()
            if result and result.flag
        ]
        
        high_risk_campaigns = [
            campaign_id for campaign_id, result in results.items()
            if result and result.risk_score > 0.2
        ]
        
        return {
            "total_campaigns": len(results),
            "flagged_campaigns": len(flagged_campaigns),
            "high_risk_campaigns": len(high_risk_campaigns),
            "flagged_campaign_ids": flagged_campaigns,
            "high_risk_campaign_ids": high_risk_campaigns,
            "campaign_results": results
        }
    
    def get_concentration_recommendations(
        self,
        campaign_id: str,
        goal_type: str
    ) -> List[str]:
        """
        Get recommendations for addressing concentration risk.
        
        Args:
            campaign_id: Campaign identifier
            goal_type: Campaign goal type
        
        Returns:
            List of recommendations
        """
        result = self.assess_campaign_risk(campaign_id, goal_type)
        recommendations = []
        
        if not result.flag:
            recommendations.append("Current concentration is optimal. Continue current strategy.")
            return recommendations
        
        if result.direction == "too_concentrated":
            recommendations.extend([
                "Diversify targeting across additional topic clusters",
                "Reduce budget allocation to top-performing clusters",
                "Experiment with new audience segments",
                "Increase bid diversity across platforms"
            ])
        else:
            recommendations.extend([
                "Focus budget on high-performing clusters",
                "Increase concentration in proven segments",
                "Reduce spend on underperforming clusters",
                "Consider consolidating similar audience segments"
            ])
        
        return recommendations