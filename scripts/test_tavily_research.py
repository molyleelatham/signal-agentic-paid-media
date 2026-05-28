"""
Test Tavily Research for Gymshark

Tests the Tavily research service for Reddit scraping, SEO keywords,
Google keywords, Thrad inputs, and content ideas.
"""

import sys
sys.path.insert(0, '/Users/molyleelatham/Documents/adtech-hackathon')

from services.intelligence.tavily_research import GymsharkTavilyResearch
from shared.utils.settings import settings

def test_tavily_research():
    """Test the Tavily research service."""
    print("=" * 60)
    print("Testing Tavily Research for Gymshark")
    print("=" * 60)
    print()
    
    # Check for Tavily API key
    tavily_api_key = settings.tavily_api_key
    
    if not tavily_api_key:
        print("❌ TAVILY_API_KEY not configured")
        print("Please set TAVILY_API_KEY in .env.local")
        return
    
    print(f"✅ TAVILY_API_KEY configured")
    print()
    
    # Initialize research service
    research_service = GymsharkTavilyResearch(tavily_api_key=tavily_api_key)
    
    if not research_service.available:
        print("❌ Tavily not available")
        print("Install with: pip install tavily-python")
        return
    
    print("✅ Tavily service initialized")
    print()
    
    # Perform comprehensive research
    print("Performing comprehensive research...")
    print("-" * 60)
    
    try:
        research_result = research_service.perform_comprehensive_research(
            base_query="Gymshark fitness apparel",
            max_results_per_source=5,  # Reduced for testing
            time_range="month"
        )
        
        print(f"\n✅ Research complete!")
        print()
        
        # Display summary
        print("Research Summary:")
        print("-" * 60)
        print(research_result.summary)
        print()
        
        # Display Reddit posts
        print(f"Reddit Posts ({len(research_result.reddit_posts)}):")
        print("-" * 60)
        for i, post in enumerate(research_result.reddit_posts[:3], 1):
            print(f"{i}. r/{post.subreddit}: {post.title[:60]}...")
            print(f"   Score: {post.score}, Comments: {post.comments_count}")
            print(f"   Keywords: {', '.join(post.keywords[:5])}")
            print()
        
        # Display SEO keywords
        print(f"SEO Keywords ({len(research_result.seo_keywords)}):")
        print("-" * 60)
        for i, kw in enumerate(research_result.seo_keywords[:5], 1):
            print(f"{i}. {kw.keyword} ({kw.intent}, difficulty: {kw.difficulty:.2f})")
        print()
        
        # Display Google keywords
        print(f"Google Keywords for Bidding ({len(research_result.google_keywords)}):")
        print("-" * 60)
        for i, kw in enumerate(research_result.google_keywords[:5], 1):
            print(f"{i}. {kw.keyword} ({kw.match_type}, bid: £{kw.bid_suggestion}, {kw.competition} competition)")
        print()
        
        # Display Thrad inputs
        print(f"Thrad BERT Inputs ({len(research_result.thrad_inputs)}):")
        print("-" * 60)
        for i, inp in enumerate(research_result.thrad_inputs[:5], 1):
            print(f"{i}. {inp.query} (Category: {inp.category}, Confidence: {inp.confidence:.2f})")
        print()
        
        # Display content ideas
        print(f"Content Ideas ({len(research_result.content_ideas)}):")
        print("-" * 60)
        for i, idea in enumerate(research_result.content_ideas[:5], 1):
            print(f"{i}. {idea.topic} for {idea.platform} ({idea.content_type})")
            print(f"   Score: {idea.opportunity_score:.2f}")
            print(f"   Angle: {idea.angle[:60]}...")
        print()
        
        print("=" * 60)
        print("Test Complete!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_tavily_research()