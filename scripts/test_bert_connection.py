"""
Test BERT Model Connection

Tests the connection to the Thrad BERT model for keyword classification.
"""

import sys
sys.path.insert(0, '/Users/molyleelatham/Documents/adtech-hackathon')

def test_thrad_bert_connection():
    """Test connection to Thrad BERT model."""
    print("=" * 60)
    print("Testing Thrad BERT Model Connection")
    print("=" * 60)
    print()
    
    # Check for Thrad API key
    from shared.utils.settings import settings
    
    thrad_api_key = settings.thrad_api_key
    
    if thrad_api_key:
        print(f"✅ THRAD_API_KEY configured: {thrad_api_key[:20]}...")
    else:
        print("⚠️  THRAD_API_KEY not configured")
        print("   Will test with mock/local model if available")
    print()
    
    # Test Thrad BERT client
    print("Testing Thrad BERT Client...")
    print("-" * 60)
    
    try:
        from services.intelligence.thrad_bert_client import ThradBERTClient
        
        # Initialize client (demo mode for testing without actual model)
        client = ThradBERTClient(demo_mode=True)
        
        print("✅ Thrad BERT Client initialized (demo mode)")
        print()
        
        # Test keyword analysis with sample keywords
        test_keywords = [
            "gymshark leggings",
            "fitness workout routine",
            "buy gym clothes online",
            "how to build muscle",
            "cheap gym equipment"
        ]
        
        print("Testing keyword analysis...")
        print("-" * 60)
        
        try:
            import asyncio
            
            # Run async method
            analyses = asyncio.run(client.analyze_keywords(test_keywords, topic="Gymshark Fitness"))
            
            for keyword, analysis in zip(test_keywords, analyses):
                print(f"✅ '{keyword}' → Category: {analysis.category}, Relevance: {analysis.relevance_score:.2f}, Intent: {analysis.intent_score:.2f}")
                print(f"   Suggested bid: £{analysis.suggested_bid:.2f}")
            
        except Exception as e:
            print(f"❌ Keyword analysis error: {e}")
        
        print()
        
        # Test generating keywords from intelligence
        print("Testing keyword generation from intelligence...")
        print("-" * 60)
        
        sample_intelligence = {
            "results": [
                {
                    "title": "Gymshark Leggings Review",
                    "content": "Gymshark is trending with their new seamless leggings. Users love the fit and quality."
                },
                {
                    "title": "Fitness Tips for Beginners",
                    "content": "Starting a fitness journey requires the right gear and mindset."
                }
            ]
        }
        
        try:
            keywords = asyncio.run(client.generate_keywords_from_intelligence(
                sample_intelligence,
                topic="Gymshark Fitness",
                max_keywords=5
            ))
            
            print(f"✅ Generated {len(keywords)} keywords:")
            for kw in keywords:
                print(f"   - {kw}")
            
        except Exception as e:
            print(f"❌ Keyword generation error: {e}")
        
        print()
        
    except ImportError as e:
        print(f"❌ Thrad BERT Client not available: {e}")
        print("   Install required dependencies")
    except Exception as e:
        print(f"❌ Error initializing Thrad BERT Client: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test DisBERT Thrad classification
    print("Testing DisBERT Thrad Classification...")
    print("-" * 60)
    
    try:
        from services.intelligence.disbert_thrad_classification import DisBERTThradAdIntegrator
        
        integrator = DisBERTThradAdIntegrator()
        
        print("✅ DisBERT Thrad AdIntegrator initialized")
        print()
        
        # Test classification with sample queries
        test_queries = [
            "gymshark leggings review",
            "best workout routine for beginners",
            "buy gymshark online",
            "how to start fitness journey"
        ]
        
        print("Testing query classification...")
        print("-" * 60)
        
        for query in test_queries:
            try:
                result = integrator.classify_query_with_disbert(query)
                print(f"✅ '{query}' → Category: {result.value}")
                
                # Get keyword strategy for this classification
                strategy = integrator.get_google_ads_keywords_for_classification(result)
                if strategy:
                    print(f"   Use as keywords: {strategy.use_as_keywords}")
                    print(f"   Keywords: {strategy.keywords[:3]}")
                    print(f"   Commercial intent: {strategy.commercial_intent:.2f}")
                
                # Get ingestion rule
                rule = integrator.get_ingestion_rule_for_classification(result)
                if rule:
                    print(f"   Should ingest: {rule.should_ingest} (priority: {rule.ingestion_priority})")
                
            except Exception as e:
                print(f"❌ '{query}' → Error: {e}")
            print()
        
        print()
        
    except ImportError as e:
        print(f"❌ DisBERT Thrad Classification not available: {e}")
    except Exception as e:
        print(f"❌ Error with DisBERT: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)
    print("Test Complete!")
    print("=" * 60)


def test_local_bert_model():
    """Test local BERT model if available."""
    print()
    print("=" * 60)
    print("Testing Local BERT Model (if available)")
    print("=" * 60)
    print()
    
    try:
        from transformers import pipeline
        
        print("✅ Transformers library available")
        print()
        
        # Try to load a simple BERT model for QA
        print("Loading BERT model for question answering...")
        print("-" * 60)
        
        try:
            # Use a lightweight model
            qa_pipeline = pipeline(
                "question-answering",
                model="distilbert-base-cased-distilled-squad",
                device=-1  # CPU
            )
            
            print("✅ BERT model loaded successfully")
            print()
            
            # Test with a simple question
            context = """
            Gymshark is a fitness apparel brand founded in 2012.
            They specialize in gym wear, leggings, and fitness accessories.
            Their products are popular among fitness enthusiasts.
            """
            
            test_questions = [
                "When was Gymshark founded?",
                "What does Gymshark specialize in?",
                "Who are Gymshark's products popular with?"
            ]
            
            print("Testing question answering...")
            print("-" * 60)
            
            for question in test_questions:
                result = qa_pipeline(question=question, context=context)
                print(f"Q: {question}")
                print(f"A: {result['answer']} (confidence: {result['score']:.2f})")
                print()
            
        except Exception as e:
            print(f"❌ Error loading BERT model: {e}")
            print("   This is expected if model download fails or is slow")
        
    except ImportError:
        print("❌ Transformers library not installed")
        print("   Install with: pip install transformers torch")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    test_thrad_bert_connection()
    test_local_bert_model()