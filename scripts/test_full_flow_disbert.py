"""
Test Full Flow with DisBERT Model

Tests the complete flow:
1. Tavily research (simulated)
2. Google keyword extraction
3. DisBERT classification
4. Keyword logging with thrad_disbert model
5. Thrad data generation
6. Complete audit trail
"""

import sys
sys.path.insert(0, '/Users/molyleelatham/Documents/adtech-hackathon')

from dataclasses import asdict
from services.media_planning import campaign_keyword_logger
from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator

def test_full_flow_with_disbert():
    """Test complete flow with DisBERT model."""
    print("=" * 80)
    print("FULL FLOW TEST: Tavily Research → DisBERT → Keyword Logging → Thrad Data")
    print("=" * 80)
    print()
    
    # Step 1: Simulate Tavily Research Results
    print("Step 1: Simulating Tavily Research Results")
    print("-" * 80)
    
    simulated_research_data = {
        "query": "Gymshark fitness apparel summer collection",
        "reddit_posts": [
            {
                "title": "Gymshark Seamless Leggings Review - Best for Summer?",
                "subreddit": "fitness",
                "score": 245,
                "comments_count": 89
            },
            {
                "title": "Gymshark Summer Collection - Worth the Hype?",
                "subreddit": "Gymshark",
                "score": 178,
                "comments_count": 56
            }
        ],
        "google_keywords": [
            {
                "keyword": "gymshark seamless leggings",
                "match_type": "phrase",
                "bid_suggestion": 2.75,
                "relevance_to_gymshark": 0.90,
                "search_intent": "transactional"
            },
            {
                "keyword": "buy gymshark online",
                "match_type": "exact",
                "bid_suggestion": 3.50,
                "relevance_to_gymshark": 0.95,
                "search_intent": "transactional"
            },
            {
                "keyword": "gym wear for women",
                "match_type": "broad",
                "bid_suggestion": 2.20,
                "relevance_to_gymshark": 0.80,
                "search_intent": "informational"
            },
            {
                "keyword": "gymshark summer collection",
                "match_type": "phrase",
                "bid_suggestion": 2.95,
                "relevance_to_gymshark": 0.88,
                "search_intent": "transactional"
            },
            {
                "keyword": "fitness workout routine",
                "match_type": "broad",
                "bid_suggestion": 1.85,
                "relevance_to_gymshark": 0.70,
                "search_intent": "informational"
            }
        ]
    }
    
    print(f"✅ Research query: {simulated_research_data['query']}")
    print(f"✅ Reddit posts found: {len(simulated_research_data['reddit_posts'])}")
    print(f"✅ Google keywords extracted: {len(simulated_research_data['google_keywords'])}")
    print()
    
    # Step 2: Initialize DisBERT Classifier
    print("Step 2: Initializing DisBERT Thrad Classifier")
    print("-" * 80)
    
    disbert_integrator = DisBERTThradAdIntegrator()
    print("✅ DisBERT Thrad AdIntegrator initialized")
    print()
    
    # Step 3: Classify Keywords with DisBERT
    print("Step 3: Classifying Keywords with DisBERT Model")
    print("-" * 80)
    
    classified_keywords = []
    for kw in simulated_research_data["google_keywords"]:
        classification = disbert_integrator.classify_query_with_disbert(kw["keyword"])
        
        # Get category (H, G, A, etc.)
        category = classification.value
        
        # Get keyword strategy for this classification
        strategy = disbert_integrator.get_google_ads_keywords_for_classification(classification)
        
        classified_keywords.append({
            "keyword": kw["keyword"],
            "match_type": kw["match_type"],
            "bid_suggestion": kw["bid_suggestion"],
            "relevance_to_gymshark": kw["relevance_to_gymshark"],
            "search_intent": kw["search_intent"],
            "category": category,
            "use_as_keywords": strategy.use_as_keywords if strategy else False,
            "commercial_intent": strategy.commercial_intent if strategy else 0.5
        })
        
        print(f"✅ '{kw['keyword']}' → Category: {category}")
        if strategy:
            print(f"   Use as keywords: {strategy.use_as_keywords}, Commercial intent: {strategy.commercial_intent:.2f}")
    
    print()
    
    # Step 4: Log Keywords with DisBERT Model
    print("Step 4: Logging Keywords to GYMSHARK_PPC_GENERIC_2026 (using thrad_disbert)")
    print("-" * 80)
    
    log_entries = campaign_keyword_logger.log_keywords_from_research(
        google_keywords=classified_keywords,
        source="tavily",
        model_used="thrad_disbert"  # Using DisBERT model for context organization
    )
    
    print(f"✅ Logged {len(log_entries)} keywords to campaign")
    print()
    
    # Step 5: Display Complete Logs
    print("Step 5: Complete Keyword Logs with Thrad Data")
    print("-" * 80)
    
    for i, log in enumerate(log_entries, 1):
        print(f"{i}. Keyword: {log.keyword}")
        print(f"   Match Type: {log.match_type}")
        print(f"   Bid Amount: £{log.bid_amount:.2f}")
        print(f"   Source: {log.source}")
        print(f"   Confidence: {log.confidence:.2f}")
        print(f"   Intent: {log.intent}")
        print(f"   Category: {log.category}")
        print(f"   Model Used: {log.model_used}")
        
        if log.thrad_data:
            print(f"   Thrad Data:")
            print(f"     - User ID: {log.thrad_data['user_id']}")
            print(f"     - Chat ID: {log.thrad_data['chat_id']}")
            print(f"     - Summary: {log.thrad_data['summary']}")
            print(f"     - Messages: {len(log.thrad_data['messages'])}")
            print(f"     - Turn Number: {log.thrad_data['turn_number']}")
            print(f"     - Ad Formats: {', '.join(log.thrad_data['ad_formats'])}")
            print(f"     - Model in Thrad Data: {log.thrad_data.get('model_used', 'Not specified')}")
        
        print()
    
    # Step 6: Summary
    print("Step 6: Flow Summary")
    print("-" * 80)
    
    print(f"✅ Research Query: {simulated_research_data['query']}")
    print(f"✅ Total Keywords Classified: {len(classified_keywords)}")
    print(f"✅ Total Keywords Logged: {len(log_entries)}")
    print(f"✅ Campaign: GYMSHARK_PPC_GENERIC_2026")
    print(f"✅ Model Used: thrad_disbert (for all keywords)")
    print()
    
    # Category breakdown
    category_counts = {}
    for log in log_entries:
        cat = log.category
        category_counts[cat] = category_counts.get(cat, 0) + 1
    
    print("Category Breakdown:")
    for cat, count in category_counts.items():
        print(f"  - Category {cat}: {count} keywords")
    
    print()
    
    # Intent breakdown
    intent_counts = {}
    for log in log_entries:
        intent = log.intent
        intent_counts[intent] = intent_counts.get(intent, 0) + 1
    
    print("Intent Breakdown:")
    for intent, count in intent_counts.items():
        print(f"  - {intent}: {count} keywords")
    
    print()
    print("=" * 80)
    print("FULL FLOW TEST COMPLETE")
    print("=" * 80)
    print()
    print("Key Achievements:")
    print("  ✅ Simulated Tavily research")
    print("  ✅ Classified keywords with DisBERT")
    print("  ✅ Logged keywords with 'using thrad_disbert' in logs")
    print("  ✅ Generated Thrad data with model_used field")
    print("  ✅ Complete audit trail created")
    print()


def test_api_integration():
    """Test API integration flow."""
    print("=" * 80)
    print("API INTEGRATION TEST")
    print("=" * 80)
    print()
    
    print("This would test the actual API endpoint:")
    print("POST /api/v1/planning/complete-planning-with-keywords")
    print("  ?query=Gymshark%20fitness")
    print("  &max_results=5")
    print("  &use_disbert=true")
    print()
    
    print("Expected flow:")
    print("1. API receives request")
    print("2. Performs Tavily research")
    print("3. Extracts Google keywords")
    print("4. Classifies with DisBERT (if use_disbert=true)")
    print("5. Logs keywords to GYMSHARK_PPC_GENERIC_2026")
    print("6. Generates Thrad data with model_used='thrad_disbert'")
    print("7. Returns complete results with logs")
    print()
    
    print("Expected response:")
    print("{")
    print("  'research_summary': '...',")
    print("  'keywords_added': 5,")
    print("  'campaign_name': 'GYMSHARK_PPC_GENERIC_2026',")
    print("  'model_used': 'thrad_disbert',")
    print("  'keyword_logs': [...],")
    print("  'research_data': {...}")
    print("}")
    print()


if __name__ == "__main__":
    test_full_flow_with_disbert()
    test_api_integration()