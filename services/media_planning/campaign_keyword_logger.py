"""
Campaign Keyword Logger

Logs keywords added to campaigns and generates Thrad data for tracking.
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict, field
import json
import random


@dataclass
class ThradMessage:
    """Thrad message data."""
    role: str
    content: str
    timestamp: str


@dataclass
class ThradConfig:
    """Thrad configuration."""
    ad_offset: int
    max_frequency: int
    max_headline_chars: int
    experiment_tag: str


@dataclass
class ThradUserMetadata:
    """Thrad user metadata."""
    age_range: str
    gender: Optional[str] = None
    location: Optional[str] = None
    interests: Optional[List[str]] = None


@dataclass
class ThradData:
    """Complete Thrad data structure."""
    user_id: str
    chat_id: str
    messages: List[ThradMessage]
    summary: str
    config: ThradConfig
    user_metadata: ThradUserMetadata
    turn_number: int
    ad_formats: List[str]
    force: bool
    model_used: Optional[str] = None  # "thrad_disbert" or None


@dataclass
class KeywordAddLog:
    """Log entry for keyword added to campaign."""
    timestamp: str
    campaign_name: str
    keyword: str
    match_type: str
    bid_amount: float
    source: str  # tavily, manual, bert, thrad
    confidence: float
    intent: str
    category: Optional[str] = None
    model_used: Optional[str] = None  # "thrad_disbert" or None
    thrad_data: Optional[Dict] = None


class CampaignKeywordLogger:
    """
    Logs keywords added to campaigns and generates Thrad tracking data.
    
    This service:
    - Logs when keywords are added to GYMSHARK_PPC_GENERIC_2026 campaign
    - Generates fake Thrad data for tracking
    - Integrates with Tavily research and BERT classification
    - Provides audit trail for keyword additions
    """
    
    def __init__(self):
        """Initialize campaign keyword logger."""
        self.logs: List[KeywordAddLog] = []
        self.target_campaign = "GYMSHARK_PPC_GENERIC_2026"
    
    def log_keyword_addition(
        self,
        keyword: str,
        match_type: str,
        bid_amount: float,
        source: str,
        confidence: float,
        intent: str,
        category: Optional[str] = None,
        model_used: Optional[str] = None
    ) -> KeywordAddLog:
        """
        Log a keyword addition to the campaign.
        
        Args:
            keyword: The keyword being added
            match_type: Match type (broad, phrase, exact)
            bid_amount: Bid amount in GBP
            source: Source of the keyword (tavily, manual, bert, thrad)
            confidence: Confidence score (0-1)
            intent: Search intent (informational, transactional, navigational)
            category: Optional category from BERT/Thrad classification
            model_used: Model used for context organization (e.g., "thrad_disbert")
            
        Returns:
            KeywordAddLog entry
        """
        log_entry = KeywordAddLog(
            timestamp=datetime.now().isoformat(),
            campaign_name=self.target_campaign,
            keyword=keyword,
            match_type=match_type,
            bid_amount=bid_amount,
            source=source,
            confidence=confidence,
            intent=intent,
            category=category,
            model_used=model_used,
            thrad_data=None  # Will be populated if needed
        )
        
        self.logs.append(log_entry)
        
        # Build log message with model information
        model_msg = f" (using {model_used})" if model_used else ""
        print(f"[LOG] Added keyword '{keyword}' to {self.target_campaign}{model_msg}")
        print(f"      Match: {match_type}, Bid: £{bid_amount}, Source: {source}, Category: {category}")
        
        return log_entry
    
    def generate_thrad_data(
        self,
        keyword: str,
        user_context: Optional[Dict] = None,
        model_used: Optional[str] = None
    ) -> ThradData:
        """
        Generate fake Thrad data for tracking.
        
        Args:
            keyword: The keyword being tracked
            user_context: Optional user context for personalization
            model_used: Model used for context organization (e.g., "thrad_disbert")
            
        Returns:
            ThradData structure
        """
        # Generate fake user and chat IDs
        user_id = f"user_{random.randint(1000, 9999)}"
        chat_id = f"chat_{random.randint(1000, 9999)}"
        
        # Generate fake conversation messages
        messages = self._generate_fake_messages(keyword)
        
        # Generate summary
        summary = self._generate_summary(keyword, messages)
        
        # Generate config
        config = ThradConfig(
            ad_offset=random.randint(1, 5),
            max_frequency=random.randint(3, 7),
            max_headline_chars=random.randint(50, 70),
            experiment_tag=random.choice(["variant_a", "variant_b", "control"])
        )
        
        # Generate user metadata
        user_metadata = self._generate_user_metadata(user_context)
        
        # Generate turn number
        turn_number = random.randint(1, 10)
        
        # Generate ad formats
        ad_formats = random.sample(
            ["sponsored_message", "banner", "video", "carousel"],
            k=random.randint(1, 3)
        )
        
        return ThradData(
            user_id=user_id,
            chat_id=chat_id,
            messages=messages,
            summary=summary,
            config=config,
            user_metadata=user_metadata,
            turn_number=turn_number,
            ad_formats=ad_formats,
            force=False,
            model_used=model_used
        )
    
    def _generate_fake_messages(self, keyword: str) -> List[ThradMessage]:
        """Generate fake conversation messages based on keyword."""
        base_time = datetime.now()
        
        # Generate relevant messages based on keyword intent
        if any(word in keyword.lower() for word in ["buy", "purchase", "shop", "price"]):
            # Transactional intent
            messages = [
                ThradMessage(
                    role="user",
                    content=f"Looking for {keyword}",
                    timestamp=(base_time).isoformat()
                ),
                ThradMessage(
                    role="assistant",
                    content=f"What's your budget for {keyword}?",
                    timestamp=(base_time).isoformat()
                ),
                ThradMessage(
                    role="user",
                    content="Around £50-100",
                    timestamp=(base_time).isoformat()
                ),
                ThradMessage(
                    role="assistant",
                    content=f"I found some great options for {keyword} in that range",
                    timestamp=(base_time).isoformat()
                )
            ]
        else:
            # Informational intent
            messages = [
                ThradMessage(
                    role="user",
                    content=f"Tell me about {keyword}",
                    timestamp=(base_time).isoformat()
                ),
                ThradMessage(
                    role="assistant",
                    content=f"Here's what you need to know about {keyword}",
                    timestamp=(base_time).isoformat()
                ),
                ThradMessage(
                    role="user",
                    content="What are the key features?",
                    timestamp=(base_time).isoformat()
                ),
                ThradMessage(
                    role="assistant",
                    content=f"The key features for {keyword} include quality, durability, and style",
                    timestamp=(base_time).isoformat()
                )
            ]
        
        return messages
    
    def _generate_summary(self, keyword: str, messages: List[ThradMessage]) -> str:
        """Generate a summary of the conversation."""
        user_messages = [m for m in messages if m.role == "user"]
        
        if user_messages:
            first_intent = user_messages[0].content
            return f"User is interested in {keyword}. Initial query: {first_intent[:50]}..."
        else:
            return f"Conversation about {keyword}"
    
    def _generate_user_metadata(self, user_context: Optional[Dict] = None) -> ThradUserMetadata:
        """Generate user metadata."""
        if user_context:
            return ThradUserMetadata(
                age_range=user_context.get("age_range", "25-34"),
                gender=user_context.get("gender"),
                location=user_context.get("location"),
                interests=user_context.get("interests")
            )
        else:
            # Generate fake metadata
            age_ranges = ["18-24", "25-34", "35-44", "45-54", "55-64"]
            return ThradUserMetadata(
                age_range=random.choice(age_ranges),
                gender=random.choice(["male", "female", None]),
                location=random.choice(["UK", "US", "EU", None]),
                interests=random.sample(
                    ["fitness", "gym", "running", "yoga", "nutrition", "wellness"],
                    k=random.randint(1, 3)
                )
            )
    
    def log_keywords_from_research(
        self,
        google_keywords: List[Dict],
        source: str = "tavily",
        model_used: Optional[str] = None
    ) -> List[KeywordAddLog]:
        """
        Log multiple keywords from research data.
        
        Args:
            google_keywords: List of Google keyword dictionaries
            source: Source of the keywords
            model_used: Model used for context organization (e.g., "thrad_disbert")
            
        Returns:
            List of log entries
        """
        log_entries = []
        
        for kw_data in google_keywords:
            log_entry = self.log_keyword_addition(
                keyword=kw_data.get("keyword", ""),
                match_type=kw_data.get("match_type", "phrase"),
                bid_amount=kw_data.get("bid_suggestion", 2.0),
                source=source,
                confidence=kw_data.get("relevance_to_gymshark", 0.7),
                intent=kw_data.get("search_intent", "informational"),
                category=kw_data.get("category"),
                model_used=model_used
            )
            
            # Generate Thrad data for tracking
            thrad_data = self.generate_thrad_data(
                kw_data.get("keyword", ""),
                model_used=model_used
            )
            log_entry.thrad_data = asdict(thrad_data)
            
            log_entries.append(log_entry)
        
        return log_entries
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        """Get recent logs."""
        recent_logs = self.logs[-limit:] if limit else self.logs
        return [asdict(log) for log in recent_logs]
    
    def get_logs_by_campaign(self, campaign_name: str, limit: int = 50) -> List[Dict]:
        """Get logs for a specific campaign."""
        campaign_logs = [log for log in self.logs if log.campaign_name == campaign_name]
        recent_logs = campaign_logs[-limit:] if limit else campaign_logs
        return [asdict(log) for log in recent_logs]
    
    def get_logs_by_source(self, source: str, limit: int = 50) -> List[Dict]:
        """Get logs by source."""
        source_logs = [log for log in self.logs if log.source == source]
        recent_logs = source_logs[-limit:] if limit else source_logs
        return [asdict(log) for log in recent_logs]
    
    def clear_logs(self):
        """Clear all logs."""
        self.logs = []
    
    def export_logs(self, filepath: str):
        """Export logs to JSON file."""
        with open(filepath, 'w') as f:
            json.dump(self.get_logs(), f, indent=2)
        print(f"Exported {len(self.logs)} logs to {filepath}")


# Global logger instance
campaign_keyword_logger = CampaignKeywordLogger()