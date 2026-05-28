"""
DisBERT Thrad Classification Integration for Ad Platform

This module integrates the DisBERT Thrad model's classification system (A-M)
with Google Ads keyword targeting and content ingestion back into the Thrad LLM platform.

Classification System (DisBERT Thrad):
A - academic_help
B - personal_writing_or_communication
C - writing_and_editing
D - creative_writing_and_role_play
E - general_guidance_and_info (HIGH PRIORITY for ingestion)
F - programming_and_data_analysis
G - creative_ideation
H - purchasable_products (HIGH VALUE for ads)
I - greetings_and_chitchat
J - relationships_and_personal_reflection (HIGHEST PRIORITY for ingestion)
K - media_generation_or_analysis
L - other
M - other_obscene_or_illegal (BLOCK)
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DisBERTThradClassification(Enum):
    """
    DisBERT Thrad model classification system.
    """
    ACADEMIC_HELP = "A"
    PERSONAL_WRITING_COMMUNICATION = "B"
    WRITING_AND_EDITING = "C"
    CREATIVE_WRITING_ROLE_PLAY = "D"
    GENERAL_GUIDANCE_INFO = "E"  # HIGH PRIORITY for ingestion
    PROGRAMMING_DATA_ANALYSIS = "F"
    CREATIVE_IDEATION = "G"
    PURCHASABLE_PRODUCTS = "H"  # HIGH VALUE for ads
    GREETINGS_CHITCHAT = "I"
    RELATIONSHIPS_PERSONAL_REFLECTION = "J"  # HIGHEST PRIORITY for ingestion
    MEDIA_GENERATION_ANALYSIS = "K"
    OTHER = "L"
    OTHER_OBSCENE_ILLEGAL = "M"  # BLOCK


@dataclass
class GoogleAdsKeywordStrategy:
    """Strategy for using DisBERT classifications as Google Ads keywords."""
    classification: DisBERTThradClassification
    classification_name: str
    
    # Should this classification be used as keywords?
    use_as_keywords: bool
    
    # Keywords derived from classification
    keywords: List[str]
    
    # Negative keywords to block
    negative_keywords: List[str]
    
    # Bid multiplier (1.0 = baseline, higher = more competitive)
    bid_multiplier: float
    
    # Commercial intent score (0-1)
    commercial_intent: float


@dataclass
class ThradPlatformIngestionRule:
    """Rule for ingesting classified content back into Thrad LLM platform ads."""
    classification: DisBERTThradClassification
    classification_name: str
    
    # Should this be ingested back into the platform?
    should_ingest: bool
    
    # Priority for ingestion (1-10, higher = more important)
    ingestion_priority: int
    
    # What type of content to ingest
    content_type: str  # training_data, user_examples, successful_prompts, ad_copy
    
    # How to use in ads
    ad_usage: str  # targeting, creative, optimization, audience_segmentation
    
    # Filtering rules
    filtering_rules: List[str]


class DisBERTThradAdIntegrator:
    """
    Integrates DisBERT Thrad classifications with Google Ads and Thrad platform.
    
    Key Decisions:
    1. Which classifications to use as Google Ads keywords?
       - H (purchasable_products): YES - Highest commercial intent
       - A (academic_help): YES - High commercial value
       - F (programming_data_analysis): YES - High commercial value
       - C (writing_and_editing): YES - Commercial service
       - E (general_guidance_and_info): YES - Discovery stage
       - Others: Selective based on use case
    
    2. Which to ingest back into Thrad LLM platform for ads?
       - J (relationships_and_personal_reflection): YES - Priority 10 (Highest)
       - E (general_guidance_and_info): YES - Priority 9 (High)
       - H (purchasable_products): YES - Priority 8 (Conversion optimization)
       - F (programming_data_analysis): YES - Priority 7 (Technical)
       - M (other_obscene_or_illegal): NO - Block entirely
    """
    
    def __init__(self):
        """Initialize DisBERT Thrad ad integrator."""
        self.keyword_strategies = self._build_keyword_strategies()
        self.ingestion_rules = self._build_ingestion_rules()
    
    def _build_keyword_strategies(self) -> Dict[DisBERTThradClassification, GoogleAdsKeywordStrategy]:
        """
        Build Google Ads keyword strategies for each DisBERT classification.
        
        ANSWER: Which classifications to use as keywords?
        """
        return {
            # A - Academic Help: USE as keywords (high commercial value)
            DisBERTThradClassification.ACADEMIC_HELP: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.ACADEMIC_HELP,
                classification_name="academic_help",
                use_as_keywords=True,
                keywords=[
                    "homework help", "assignment assistance", "test prep",
                    "academic tutoring", "study help", "essay writing service",
                    "get homework answers", "online tutoring", "academic writing help"
                ],
                negative_keywords=["free homework", "cheat", "plagiarism"],
                bid_multiplier=1.3,
                commercial_intent=0.85
            ),
            
            # B - Personal Writing: USE as keywords
            DisBERTThradClassification.PERSONAL_WRITING_COMMUNICATION: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.PERSONAL_WRITING_COMMUNICATION,
                classification_name="personal_writing_or_communication",
                use_as_keywords=True,
                keywords=[
                    "email writing assistant", "professional email help",
                    "message writing service", "communication coach",
                    "letter writing help", "workplace communication assistant"
                ],
                negative_keywords=["free email", "spam"],
                bid_multiplier=1.2,
                commercial_intent=0.75
            ),
            
            # C - Writing and Editing: USE as keywords
            DisBERTThradClassification.WRITING_AND_EDITING: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.WRITING_AND_EDITING,
                classification_name="writing_and_editing",
                use_as_keywords=True,
                keywords=[
                    "editing service", "proofreading help", "document editor",
                    "content writing service", "writing coach", "professional editing"
                ],
                negative_keywords=["free editing"],
                bid_multiplier=1.25,
                commercial_intent=0.80
            ),
            
            # D - Creative Writing: SELECTIVE use
            DisBERTThradClassification.CREATIVE_WRITING_ROLE_PLAY: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.CREATIVE_WRITING_ROLE_PLAY,
                classification_name="creative_writing_and_role_play",
                use_as_keywords=True,
                keywords=[
                    "story writing assistant", "creative writing help",
                    "fiction writing service", "script writing assistance"
                ],
                negative_keywords=["free stories"],
                bid_multiplier=1.1,
                commercial_intent=0.60
            ),
            
            # E - General Guidance: USE as keywords (discovery stage)
            DisBERTThradClassification.GENERAL_GUIDANCE_INFO: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.GENERAL_GUIDANCE_INFO,
                classification_name="general_guidance_and_info",
                use_as_keywords=True,
                keywords=[
                    "how to help", "step by step guide", "practical advice",
                    "information assistance", "guidance platform", "expert advice"
                ],
                negative_keywords=["free advice", "free guide"],
                bid_multiplier=1.15,
                commercial_intent=0.55
            ),
            
            # F - Programming: USE as keywords (high commercial value)
            DisBERTThradClassification.PROGRAMMING_DATA_ANALYSIS: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.PROGRAMMING_DATA_ANALYSIS,
                classification_name="programming_and_data_analysis",
                use_as_keywords=True,
                keywords=[
                    "code help", "programming assistance", "debug service",
                    "data analysis help", "coding assistant", "programming tutor"
                ],
                negative_keywords=["free code", "code cheat"],
                bid_multiplier=1.4,  # Highest commercial value
                commercial_intent=0.90
            ),
            
            # G - Creative Ideation: SELECTIVE use
            DisBERTThradClassification.CREATIVE_IDEATION: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.CREATIVE_IDEATION,
                classification_name="creative_ideation",
                use_as_keywords=True,
                keywords=[
                    "idea generation", "brainstorming assistance", "concept development",
                    "creative thinking help", "innovation consulting"
                ],
                negative_keywords=["free ideas"],
                bid_multiplier=1.0,
                commercial_intent=0.50
            ),
            
            # H - Purchasable Products: USE as keywords (HIGHEST commercial intent)
            DisBERTThradClassification.PURCHASABLE_PRODUCTS: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.PURCHASABLE_PRODUCTS,
                classification_name="purchasable_products",
                use_as_keywords=True,
                keywords=[
                    "buy ai assistant", "purchase writing service", "ai tool pricing",
                    "subscription service", "premium ai", "paid assistant",
                    "service pricing", "cost of ai", "ai subscription"
                ],
                negative_keywords=["free ai", "free tool"],
                bid_multiplier=1.5,  # HIGHEST bid multiplier
                commercial_intent=0.95  # HIGHEST commercial intent
            ),
            
            # I - Greetings: LOW priority for ads
            DisBERTThradClassification.GREETINGS_CHITCHAT: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.GREETINGS_CHITCHAT,
                classification_name="greetings_and_chitchat",
                use_as_keywords=False,  # Low commercial value
                keywords=["ai chat companion", "conversation ai"],
                negative_keywords=["free chat"],
                bid_multiplier=0.7,
                commercial_intent=0.30
            ),
            
            # J - Relationships: SELECTIVE use
            DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION,
                classification_name="relationships_and_personal_reflection",
                use_as_keywords=True,
                keywords=[
                    "relationship advice", "emotional support ai",
                    "personal reflection help", "life coaching assistance"
                ],
                negative_keywords=["free therapy", "medical advice"],
                bid_multiplier=1.0,
                commercial_intent=0.45
            ),
            
            # K - Media Generation: USE as keywords
            DisBERTThradClassification.MEDIA_GENERATION_ANALYSIS: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.MEDIA_GENERATION_ANALYSIS,
                classification_name="media_generation_or_analysis",
                use_as_keywords=True,
                keywords=[
                    "image generation ai", "video creation service",
                    "media analysis tool", "content generation ai"
                ],
                negative_keywords=["free image generator"],
                bid_multiplier=1.2,
                commercial_intent=0.75
            ),
            
            # L - Other: LOW priority
            DisBERTThradClassification.OTHER: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.OTHER,
                classification_name="other",
                use_as_keywords=False,
                keywords=["ai assistance", "digital assistant"],
                negative_keywords=["free ai"],
                bid_multiplier=0.8,
                commercial_intent=0.35
            ),
            
            # M - Obscene/Illegal: BLOCK
            DisBERTThradClassification.OTHER_OBSCENE_ILLEGAL: GoogleAdsKeywordStrategy(
                classification=DisBERTThradClassification.OTHER_OBSCENE_ILLEGAL,
                classification_name="other_obscene_or_illegal",
                use_as_keywords=False,
                keywords=[],
                negative_keywords=["obscene", "illegal", "harmful"],
                bid_multiplier=0.0,
                commercial_intent=0.0
            )
        }
    
    def _build_ingestion_rules(self) -> Dict[DisBERTThradClassification, ThradPlatformIngestionRule]:
        """
        Build ingestion rules for Thrad LLM platform.
        
        ANSWER: Which classifications to ingest back into the platform?
        
        HIGHEST PRIORITY:
        - J (relationships_and_personal_reflection): Priority 10 - Empathy training, personalization
        - E (general_guidance_and_info): Priority 9 - Knowledge base, factual accuracy
        
        HIGH PRIORITY:
        - H (purchasable_products): Priority 8 - Conversion optimization, sales training
        - F (programming_data_analysis): Priority 7 - Technical accuracy
        - C (writing_and_editing): Priority 7 - Quality improvement
        
        BLOCK:
        - M (other_obscene_or_illegal): Never ingest
        """
        return {
            DisBERTThradClassification.ACADEMIC_HELP: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.ACADEMIC_HELP,
                classification_name="academic_help",
                should_ingest=True,
                ingestion_priority=6,
                content_type="user_examples",
                ad_usage="targeting",
                filtering_rules=["no_plagiarism", "academic_integrity"]
            ),
            
            DisBERTThradClassification.PERSONAL_WRITING_COMMUNICATION: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.PERSONAL_WRITING_COMMUNICATION,
                classification_name="personal_writing_or_communication",
                should_ingest=True,
                ingestion_priority=5,
                content_type="training_data",
                ad_usage="creative",
                filtering_rules=["no_pii", "privacy_protection"]
            ),
            
            DisBERTThradClassification.WRITING_AND_EDITING: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.WRITING_AND_EDITING,
                classification_name="writing_and_editing",
                should_ingest=True,
                ingestion_priority=7,
                content_type="training_data",
                ad_usage="optimization",
                filtering_rules=["copyright_check", "quality_filter"]
            ),
            
            DisBERTThradClassification.CREATIVE_WRITING_ROLE_PLAY: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.CREATIVE_WRITING_ROLE_PLAY,
                classification_name="creative_writing_and_role_play",
                should_ingest=True,
                ingestion_priority=4,
                content_type="examples",
                ad_usage="creative",
                filtering_rules=["appropriate_content"]
            ),
            
            # E - General Guidance: HIGH PRIORITY (Priority 9)
            DisBERTThradClassification.GENERAL_GUIDANCE_INFO: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.GENERAL_GUIDANCE_INFO,
                classification_name="general_guidance_and_info",
                should_ingest=True,
                ingestion_priority=9,  # HIGH PRIORITY
                content_type="training_data",
                ad_usage="targeting",
                filtering_rules=["fact_check", "accuracy_verification", "source_validation"]
            ),
            
            DisBERTThradClassification.PROGRAMMING_DATA_ANALYSIS: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.PROGRAMMING_DATA_ANALYSIS,
                classification_name="programming_and_data_analysis",
                should_ingest=True,
                ingestion_priority=7,
                content_type="training_data",
                ad_usage="targeting",
                filtering_rules=["security_check", "no_malicious_code"]
            ),
            
            DisBERTThradClassification.CREATIVE_IDEATION: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.CREATIVE_IDEATION,
                classification_name="creative_ideation",
                should_ingest=True,
                ingestion_priority=5,
                content_type="prompts",
                ad_usage="creative",
                filtering_rules=["no_harmful_ideas"]
            ),
            
            DisBERTThradClassification.PURCHASABLE_PRODUCTS: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.PURCHASABLE_PRODUCTS,
                classification_name="purchasable_products",
                should_ingest=True,
                ingestion_priority=8,  # HIGH PRIORITY - Conversion optimization
                content_type="successful_prompts",
                ad_usage="audience_segmentation",
                filtering_rules=["no_spam", "transparency"]
            ),
            
            DisBERTThradClassification.GREETINGS_CHITCHAT: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.GREETINGS_CHITCHAT,
                classification_name="greetings_and_chitchat",
                should_ingest=True,
                ingestion_priority=3,
                content_type="examples",
                ad_usage="targeting",
                filtering_rules=["polite_conversation"]
            ),
            
            # J - Relationships: HIGHEST PRIORITY (Priority 10)
            DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION,
                classification_name="relationships_and_personal_reflection",
                should_ingest=True,
                ingestion_priority=10,  # HIGHEST PRIORITY - Empathy, personalization
                content_type="training_data",
                ad_usage="personalization",
                filtering_rules=["empathy_check", "no_harmful_advice", "professional_boundaries", "mental_health_safety"]
            ),
            
            DisBERTThradClassification.MEDIA_GENERATION_ANALYSIS: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.MEDIA_GENERATION_ANALYSIS,
                classification_name="media_generation_or_analysis",
                should_ingest=True,
                ingestion_priority=6,
                content_type="training_data",
                ad_usage="creative",
                filtering_rules=["copyright_check", "appropriate_content"]
            ),
            
            DisBERTThradClassification.OTHER: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.OTHER,
                classification_name="other",
                should_ingest=False,
                ingestion_priority=0,
                content_type="none",
                ad_usage="none",
                filtering_rules=[]
            ),
            
            # M - Obscene/Illegal: BLOCK
            DisBERTThradClassification.OTHER_OBSCENE_ILLEGAL: ThradPlatformIngestionRule(
                classification=DisBERTThradClassification.OTHER_OBSCENE_ILLEGAL,
                classification_name="other_obscene_or_illegal",
                should_ingest=False,  # BLOCK - Never ingest
                ingestion_priority=0,
                content_type="none",
                ad_usage="none",
                filtering_rules=["BLOCK_ALL"]
            )
        }
    
    def get_google_ads_keywords_for_classification(
        self,
        classification: DisBERTThradClassification
    ) -> Optional[GoogleAdsKeywordStrategy]:
        """
        Get Google Ads keywords for a specific DisBERT classification.
        
        ANSWER: Yes, use classifications as keywords based on commercial intent.
        """
        strategy = self.keyword_strategies.get(classification)
        
        if strategy and strategy.use_as_keywords:
            return strategy
        
        return None
    
    def get_ingestion_rule_for_classification(
        self,
        classification: DisBERTThradClassification
    ) -> Optional[ThradPlatformIngestionRule]:
        """
        Get ingestion rule for a specific DisBERT classification.
        
        ANSWER: E and J should definitely be ingested (Priorities 9 and 10).
        """
        rule = self.ingestion_rules.get(classification)
        
        if rule and rule.should_ingest:
            return rule
        
        return None
    
    def get_high_priority_ingestion_classifications(
        self,
        min_priority: int = 8
    ) -> List[ThradPlatformIngestionRule]:
        """
        Get high-priority classifications for Thrad platform ingestion.
        
        Returns E (Priority 9) and J (Priority 10) by default.
        """
        high_priority = []
        
        for classification, rule in self.ingestion_rules.items():
            if rule.should_ingest and rule.ingestion_priority >= min_priority:
                high_priority.append(rule)
        
        # Sort by priority (highest first)
        high_priority.sort(key=lambda x: x.ingestion_priority, reverse=True)
        
        return high_priority
    
    def generate_google_ads_campaign_from_disbert(
        self,
        target_classifications: List[DisBERTThradClassification],
        budget: float
    ) -> Dict:
        """
        Generate Google Ads campaign targeting specific DisBERT classifications.
        
        Args:
            target_classifications: List of DisBERT classifications to target
            budget: Campaign budget
        
        Returns:
            Campaign configuration with keywords from selected classifications
        """
        all_keywords = []
        all_negative_keywords = []
        classification_details = []
        
        for classification in target_classifications:
            strategy = self.get_google_ads_keywords_for_classification(classification)
            
            if not strategy:
                continue  # Skip classifications not used for keywords
            
            all_keywords.extend(strategy.keywords)
            all_negative_keywords.extend(strategy.negative_keywords)
            
            classification_details.append({
                "classification": classification.value,
                "classification_name": strategy.classification_name,
                "keyword_count": len(strategy.keywords),
                "bid_multiplier": strategy.bid_multiplier,
                "commercial_intent": strategy.commercial_intent
            })
        
        # Remove duplicates
        all_keywords = list(set(all_keywords))
        all_negative_keywords = list(set(all_negative_keywords))
        
        return {
            "target_classifications": [c.value for c in target_classifications],
            "keywords": all_keywords,
            "negative_keywords": all_negative_keywords,
            "classification_details": classification_details,
            "total_keywords": len(all_keywords),
            "total_negative_keywords": len(all_negative_keywords),
            "budget": budget,
            "recommended_bids": self._calculate_recommended_bids(classification_details, budget)
        }
    
    def _calculate_recommended_bids(
        self,
        classification_details: List[Dict],
        budget: float
    ) -> List[Dict]:
        """Calculate recommended bids based on classification commercial intent."""
        base_bid = budget * 0.01  # 1% of budget as base bid
        
        recommended = []
        
        for detail in classification_details:
            bid = base_bid * detail["bid_multiplier"]
            recommended.append({
                "classification": detail["classification"],
                "bid": round(bid, 2),
                "justification": f"Commercial intent: {detail['commercial_intent']}, Multiplier: {detail['bid_multiplier']}"
            })
        
        return recommended
    
    def classify_query_with_disbert(
        self,
        query: str
    ) -> DisBERTThradClassification:
        """
        Classify a user query using DisBERT Thrad classification system.
        
        In production, this would call the actual DisBERT model.
        For demo, uses keyword matching.
        """
        query_lower = query.lower()
        
        # Check for illegal content first
        illegal_keywords = ["illegal", "obscene", "hack", "exploit", "malware"]
        if any(keyword in query_lower for keyword in illegal_keywords):
            return DisBERTThradClassification.OTHER_OBSCENE_ILLEGAL
        
        # Check for purchase intent (H)
        purchase_keywords = ["buy", "price", "cost", "purchase", "subscription", "pay"]
        if any(keyword in query_lower for keyword in purchase_keywords):
            return DisBERTThradClassification.PURCHASABLE_PRODUCTS
        
        # Check for programming (F)
        programming_keywords = ["code", "programming", "debug", "data", "algorithm"]
        if any(keyword in query_lower for keyword in programming_keywords):
            return DisBERTThradClassification.PROGRAMMING_DATA_ANALYSIS
        
        # Check for relationships (J)
        relationship_keywords = ["relationship", "feel", "emotion", "reflect", "mental health"]
        if any(keyword in query_lower for keyword in relationship_keywords):
            return DisBERTThradClassification.RELATIONSHIPS_PERSONAL_REFLECTION
        
        # Check for general guidance (E)
        guidance_keywords = ["how to", "guide", "step by step", "help me", "advice"]
        if any(keyword in query_lower for keyword in guidance_keywords):
            return DisBERTThradClassification.GENERAL_GUIDANCE_INFO
        
        # Check for academic (A)
        academic_keywords = ["homework", "assignment", "test", "exam", "study", "tutor"]
        if any(keyword in query_lower for keyword in academic_keywords):
            return DisBERTThradClassification.ACADEMIC_HELP
        
        # Check for writing (C)
        writing_keywords = ["edit", "proofread", "write", "document"]
        if any(keyword in query_lower for keyword in writing_keywords):
            return DisBERTThradClassification.WRITING_AND_EDITING
        
        # Default
        return DisBERTThradClassification.OTHER


# Summary of Key Decisions:
# ========================
# 
# 1. GOOGLE ADS KEYWORDS (Which classifications to use?)
#    - YES: H (purchasable_products) - Highest commercial intent, bid 1.5x
#    - YES: F (programming_data_analysis) - High commercial value, bid 1.4x
#    - YES: A (academic_help) - High commercial value, bid 1.3x
#    - YES: C (writing_and_editing) - Commercial service, bid 1.25x
#    - YES: E (general_guidance_and_info) - Discovery stage, bid 1.15x
#    - YES: B, D, G, J, K - Selective use based on use case
#    - NO: I, L - Low commercial value
#    - BLOCK: M - Illegal content
#
# 2. THRAD PLATFORM INGESTION (Which to ingest back?)
#    - J (relationships_and_personal_reflection): Priority 10 (HIGHEST)
#      Reason: Empathy training, personalization, emotional intelligence
#      Use: Personalization, ad targeting
#    
#    - E (general_guidance_and_info): Priority 9 (HIGH)
#      Reason: Knowledge base, factual accuracy, discovery optimization
#      Use: Targeting, content optimization
#    
#    - H (purchasable_products): Priority 8
#      Reason: Conversion optimization, sales training
#      Use: Audience segmentation, conversion ads
#    
#    - F (programming_data_analysis): Priority 7
#      Reason: Technical accuracy
#      Use: Targeting technical audiences
#    
#    - BLOCK: M (other_obscene_or_illegal) - Never ingest