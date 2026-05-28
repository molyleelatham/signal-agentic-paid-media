"""
Thrad Contextual Bidding Integration.

This implements Module 6 from the technical spec:
- Intent-goal alignment matrix
- Contextual bid scaling based on prompt intent
- Integration with local Thrad model
"""
from typing import Dict, List

from services.intelligence.bertopic_gap_matrix import ThradIntentClassifier


class ThradContextualBid:
    """
    Thrad Contextual Bidding implementation.
    
    This implements Module 6 from the technical spec:
    - Intent-goal alignment matrix
    - Bid scaling based on prompt intent classification
    """
    
    # Intent-goal alignment matrix from Module 6.2
    INTENT_GOAL_ALIGNMENT = {
        "lead_generation": {
            "purchase_intent": 1.4,   # ready to act — bid up
            "research_intent": 0.9,   # gathering info — near-normal bid
            "awareness_intent": 0.4,   # discovery — discount
            "brand_specific_intent": 1.6    # asking about you — bid up hard
        },
        "customer_acquisition": {
            "purchase_intent": 1.6,
            "research_intent": 1.0,
            "awareness_intent": 0.5,
            "brand_specific_intent": 1.8
        },
        "brand_awareness": {
            "purchase_intent": 0.6,
            "research_intent": 1.1,
            "awareness_intent": 1.5,   # discovery — this is who you want
            "brand_specific_intent": 0.8
        },
        "retargeting": {
            "purchase_intent": 1.8,   # already warm — bid aggressively
            "research_intent": 0.5,
            "awareness_intent": 0.2,
            "brand_specific_intent": 2.0    # they're asking about you — maximum bid
        }
    }
    
    def __init__(self, thrad_classifier: ThradIntentClassifier = None):
        """
        Initialize Thrad contextual bidding.
        
        Args:
            thrad_classifier: Thrad intent classifier instance
        """
        self.thrad_classifier = thrad_classifier
    
    def calculate_intent_weight(
        self,
        prompt_intent: Dict[str, float],
        goal_type: str
    ) -> float:
        """
        Calculate intent weight for bid scaling.
        
        Args:
            prompt_intent: Dict mapping intent types to probabilities
            goal_type: Campaign goal type
        
        Returns:
            Intent weight for bid scaling
        """
        if goal_type not in self.INTENT_GOAL_ALIGNMENT:
            raise ValueError(f"Unknown goal type: {goal_type}")
        
        alignment = self.INTENT_GOAL_ALIGNMENT[goal_type]
        
        # Weighted sum of intent scores × alignment weights
        intent_weight = sum(
            prompt_intent.get(intent_type, 0.0) * alignment.get(intent_type, 1.0)
            for intent_type in alignment.keys()
        )
        
        return intent_weight
    
    def thrad_contextual_bid(
        self,
        loess_optimal: float,
        prompt_intent: Dict[str, float],
        goal_type: str
    ) -> float:
        """
        Calculate contextual bid using Thrad intent classification.
        
        Args:
            loess_optimal: Optimal bid from LOESS/DMR
            prompt_intent: Dict mapping intent types to probabilities
            goal_type: Campaign goal type
        
        Returns:
            Contextually adjusted bid
        """
        intent_weight = self.calculate_intent_weight(prompt_intent, goal_type)
        
        # intent_weight > 1.0 → bid above LOESS optimal
        # intent_weight < 1.0 → bid below
        contextual_bid = loess_optimal * intent_weight
        
        return contextual_bid
    
    def classify_prompt_intent(self, prompt: str) -> Dict[str, float]:
        """
        Classify intent of a prompt using Thrad model.
        
        Args:
            prompt: User prompt to classify
        
        Returns:
            Dict mapping intent types to probabilities
        """
        if self.thrad_classifier is None:
            # Fallback to uniform distribution if no classifier
            return {
                "purchase_intent": 0.25,
                "research_intent": 0.25,
                "awareness_intent": 0.25,
                "brand_specific_intent": 0.25
            }
        
        return self.thrad_classifier.classify_intent(prompt)
    
    def calculate_contextual_bid_from_prompt(
        self,
        loess_optimal: float,
        prompt: str,
        goal_type: str
    ) -> Dict[str, float]:
        """
        Calculate contextual bid directly from prompt text.
        
        Args:
            loess_optimal: Optimal bid from LOESS/DMR
            prompt: User prompt to classify
            goal_type: Campaign goal type
        
        Returns:
            Dict with contextual bid and breakdown
        """
        # Classify intent
        prompt_intent = self.classify_prompt_intent(prompt)
        
        # Calculate contextual bid
        contextual_bid = self.thrad_contextual_bid(
            loess_optimal,
            prompt_intent,
            goal_type
        )
        
        # Calculate intent weight for transparency
        intent_weight = self.calculate_intent_weight(prompt_intent, goal_type)
        
        return {
            "contextual_bid": contextual_bid,
            "loess_optimal": loess_optimal,
            "intent_weight": intent_weight,
            "prompt_intent": prompt_intent,
            "goal_type": goal_type
        }
    
    def get_alignment_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Get the intent-goal alignment matrix.
        
        Returns:
            The alignment matrix for all goal types
        """
        return self.INTENT_GOAL_ALIGNMENT
    
    def validate_goal_type(self, goal_type: str) -> bool:
        """
        Validate that a goal type is supported.
        
        Args:
            goal_type: Goal type to validate
        
        Returns:
            True if valid, False otherwise
        """
        return goal_type in self.INTENT_GOAL_ALIGNMENT


class ThradBidIntegrator:
    """
    High-level integration of Thrad contextual bidding with the trading engine.
    
    This provides a unified interface for incorporating Thrad intent
    classification into the bid decision pipeline.
    """
    
    def __init__(self, thrad_model_path: str = None):
        """
        Initialize Thrad bid integrator.
        
        Args:
            thrad_model_path: Path to local Thrad model
        """
        # Initialize Thrad classifier
        if thrad_model_path:
            from services.intelligence.bertopic_gap_matrix import ThradIntentClassifier
            self.thrad_classifier = ThradIntentClassifier(thrad_model_path)
        else:
            self.thrad_classifier = None
        
        # Initialize contextual bidding
        self.contextual_bid = ThradContextualBid(self.thrad_classifier)
    
    def compute_bid_with_thrad_context(
        self,
        loess_optimal: float,
        prompt: str,
        goal_type: str,
        platform: str = None
    ) -> Dict:
        """
        Compute bid with Thrad contextual adjustment.
        
        Args:
            loess_optimal: Optimal bid from LOESS/DMR
            prompt: User prompt (for Thrad platform) or context
            goal_type: Campaign goal type
            platform: Platform name (only applies to Thrad platform)
        
        Returns:
            Dict with bid calculation details
        """
        # Only apply Thrad contextual bidding for Thrad platform
        if platform and platform.lower() != "thrad":
            return {
                "final_bid": loess_optimal,
                "loess_optimal": loess_optimal,
                "contextual_adjustment": False,
                "reason": "Not a Thrad platform"
            }
        
        # Calculate contextual bid
        result = self.contextual_bid.calculate_contextual_bid_from_prompt(
            loess_optimal,
            prompt,
            goal_type
        )
        
        result["contextual_adjustment"] = True
        result["platform"] = platform or "thrad"
        
        return result
    
    def batch_compute_bids(
        self,
        bid_requests: List[Dict]
    ) -> List[Dict]:
        """
        Compute contextual bids for multiple requests.
        
        Args:
            bid_requests: List of dicts with loess_optimal, prompt, goal_type, platform
        
        Returns:
            List of bid calculation results
        """
        results = []
        for request in bid_requests:
            result = self.compute_bid_with_thrad_context(
                loess_optimal=request["loess_optimal"],
                prompt=request["prompt"],
                goal_type=request["goal_type"],
                platform=request.get("platform")
            )
            results.append(result)
        
        return results