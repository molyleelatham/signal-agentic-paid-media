"""
Test Campaign Keyword Logger and Thrad Data Generation

Tests the keyword logging system and Thrad data generation for
GYMSHARK_PPC_GENERIC_2026 campaign.
"""

import sys
sys.path.insert(0, '/Users/molyleelatham/Documents/adtech-hackathon')

from dataclasses import asdict
from services.media_planning import campaign_keyword_logger

def test_keyword_logging():
    """Test keyword logging to campaign."""
    print("=" * 60)
    print("Testing Campaign Keyword Logger")
    print("=" * 60)
    print()
    
    # Test logging individual keywords
    print("Logging individual keywords...")
    print("-" * 60)
    
    test_keywords = [
        ("gymshark leggings", "phrase", 2.50, "tavily", 0.85, "transactional", "H"),
        ("fitness workout routine", "broad", 1.80, "tavily", 0.70, "informational", "E"),
        ("buy gym clothes online", "exact", 3.20, "tavily", 0.90, "transactional", "H"),
        ("how to build muscle", "phrase", 2.10, "bert", 0.65, "informational", "E"),
        ("cheap gym equipment", "broad", 1.95, "manual", 0.60, "informational", "E")
    ]
    
    for keyword, match_type, bid, source, confidence, intent, category in test_keywords:
        # Use DisBERT model for some keywords
        model_used = "thrad_disbert" if source in ["tavily", "bert"] else None
        
        log_entry = campaign_keyword_logger.log_keyword_addition(
            keyword=keyword,
            match_type=match_type,
            bid_amount=bid,
            source=source,
            confidence=confidence,
            intent=intent,
            category=category,
            model_used=model_used
        )
        
        # Generate Thrad data with model specification
        thrad_data = campaign_keyword_logger.generate_thrad_data(
            keyword,
            model_used=model_used
        )
        log_entry.thrad_data = asdict(thrad_data)
        
        print(f"✅ Logged: '{keyword}'")
        print(f"   Campaign: {log_entry.campaign_name}")
        print(f"   Match: {match_type}, Bid: £{bid}")
        print(f"   Source: {source}, Confidence: {confidence}")
        print(f"   Intent: {intent}, Category: {category}")
        print(f"   Model Used: {log_entry.model_used}")
        print(f"   Thrad Data: user_id={thrad_data.user_id}, chat_id={thrad_data.chat_id}")
        print()
    
    print(f"Total logs: {len(campaign_keyword_logger.logs)}")
    print()


def test_thrad_data_generation():
    """Test Thrad data generation."""
    print("=" * 60)
    print("Testing Thrad Data Generation")
    print("=" * 60)
    print()
    
    test_keywords = [
        "gymshark leggings",
        "buy gym clothes online",
        "fitness tips for beginners"
    ]
    
    for keyword in test_keywords:
        print(f"Generating Thrad data for: '{keyword}'")
        print("-" * 60)
        
        thrad_data = campaign_keyword_logger.generate_thrad_data(keyword)
        
        print(f"User ID: {thrad_data.user_id}")
        print(f"Chat ID: {thrad_data.chat_id}")
        print(f"Summary: {thrad_data.summary}")
        print(f"Config: ad_offset={thrad_data.config.ad_offset}, max_frequency={thrad_data.config.max_frequency}")
        print(f"User Metadata: age_range={thrad_data.user_metadata.age_range}")
        print(f"Turn Number: {thrad_data.turn_number}")
        print(f"Ad Formats: {thrad_data.ad_formats}")
        print(f"Messages: {len(thrad_data.messages)}")
        
        # Show a few messages
        for msg in thrad_data.messages[:2]:
            print(f"  {msg.role}: {msg.content[:50]}...")
        
        print()


def test_batch_logging():
    """Test batch logging from research data."""
    print("=" * 60)
    print("Testing Batch Logging from Research Data")
    print("=" * 60)
    print()
    
    # Simulate Google keywords from research
    google_keywords = [
        {
            "keyword": "gymshark seamless leggings",
            "match_type": "phrase",
            "bid_suggestion": 2.75,
            "relevance_to_gymshark": 0.90,
            "search_intent": "transactional",
            "category": "H"
        },
        {
            "keyword": "gym wear for women",
            "match_type": "broad",
            "bid_suggestion": 2.20,
            "relevance_to_gymshark": 0.80,
            "search_intent": "informational",
            "category": "E"
        },
        {
            "keyword": "buy gymshark online",
            "match_type": "exact",
            "bid_suggestion": 3.50,
            "relevance_to_gymshark": 0.95,
            "search_intent": "transactional",
            "category": "H"
        }
    ]
    
    print(f"Logging {len(google_keywords)} keywords from research...")
    print("-" * 60)
    
    log_entries = campaign_keyword_logger.log_keywords_from_research(
        google_keywords=google_keywords,
        source="tavily",
        model_used="thrad_disbert"  # Using DisBERT model for context organization
    )
    
    for log_entry in log_entries:
        print(f"✅ '{log_entry.keyword}' → {log_entry.campaign_name}")
        print(f"   Bid: £{log_entry.bid_amount}, Intent: {log_entry.intent}")
        print(f"   Model Used: {log_entry.model_used}")
        print(f"   Thrad Data: {log_entry.thrad_data['user_id'] if log_entry.thrad_data else 'None'}")
        print()
    
    print(f"Total logs after batch: {len(campaign_keyword_logger.logs)}")
    print()


def test_log_retrieval():
    """Test retrieving logs."""
    print("=" * 60)
    print("Testing Log Retrieval")
    print("=" * 60)
    print()
    
    # Get all logs
    all_logs = campaign_keyword_logger.get_logs(limit=10)
    print(f"Total logs (last 10): {len(all_logs)}")
    
    # Get logs by campaign
    campaign_logs = campaign_keyword_logger.get_logs_by_campaign("GYMSHARK_PPC_GENERIC_2026", limit=5)
    print(f"Logs for GYMSHARK_PPC_GENERIC_2026: {len(campaign_logs)}")
    
    # Get logs by source
    tavily_logs = campaign_keyword_logger.get_logs_by_source("tavily", limit=5)
    print(f"Logs from Tavily: {len(tavily_logs)}")
    
    print()


def main():
    """Run all tests."""
    print("Campaign Keyword Logger and Thrad Data Test Suite")
    print("=" * 60)
    print()
    
    test_keyword_logging()
    test_thrad_data_generation()
    test_batch_logging()
    test_log_retrieval()
    
    print("=" * 60)
    print("Test Suite Complete!")
    print("=" * 60)
    print()
    print("Summary:")
    print(f"  - Total keyword logs: {len(campaign_keyword_logger.logs)}")
    print(f"  - Campaign: GYMSHARK_PPC_GENERIC_2026")
    print(f"  - All logs include Thrad data for tracking")
    print()


if __name__ == "__main__":
    main()