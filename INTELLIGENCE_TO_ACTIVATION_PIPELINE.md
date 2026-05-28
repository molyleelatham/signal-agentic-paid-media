# Intelligence-to-Activation Pipeline Documentation

## 🚀 Complete Integration: Tavily → Thrad BERT → Google Ads API

This document describes the complete intelligence-to-activation pipeline that connects market intelligence gathering, AI-powered keyword analysis, and automated campaign creation.

## 📊 Pipeline Overview

The pipeline consists of 5 sequential steps:

```
Tavily Scraping → Thrad BERT Analysis → Google Ads Campaign → Ad Groups & Keywords → Search Ads
```

### Step 1: Tavily Intelligence Gathering
- Scrapes market trends, consumer behavior, and competitive insights
- Returns structured intelligence with search results and AI-generated answers
- Configurable search depth and result count

### Step 2: Thrad BERT Keyword Analysis
- Uses DistilBERT model to analyze intelligence
- Generates high-quality, intent-based keywords
- Scores keywords by relevance, intent, volume, and competition
- Identifies market opportunities and consumer insights

### Step 3: Google Ads Campaign Creation
- Creates structured campaigns based on intelligence
- Sets budget, dates, and targeting parameters
- Maps campaign type to Google Ads channel types

### Step 4: Ad Group and Keyword Setup
- Groups keywords by intent (High/Medium/Broad)
- Creates ad groups with appropriate bids
- Adds keywords with calculated bids based on analysis
- Supports different match types (BROAD, PHRASE, EXACT)

### Step 5: Search Ad Creation
- Generates search ads with headlines and descriptions
- Configures ad URLs and tracking
- Sets ad status and targeting

## 🔧 API Endpoints

### 1. Complete Pipeline Execution
**Endpoint**: `POST /api/v1/demo/intelligence/complete-pipeline`

Executes the entire pipeline in one call.

**Parameters**:
- `client_id`: Client ID
- `topic`: Topic to research (e.g., "gym wear", "fitness apparel")
- `campaign_type`: Google Ads campaign type (SEARCH, DISPLAY, VIDEO, SHOPPING)
- `daily_budget`: Daily campaign budget
- `match_type`: Keyword match type (BROAD, PHRASE, EXACT)

**Example**:
```bash
curl -X POST "http://localhost:8000/api/v1/demo/intelligence/complete-pipeline?client_id=CLIENT_ID&topic=gym%20wear&campaign_type=SEARCH&daily_budget=500&match_type=PHRASE"
```

**Response**:
```json
{
  "status": "success",
  "pipeline_steps": [
    {"step": "tavily_intelligence", "status": "completed", "results_count": 15},
    {"step": "thrad_bert_analysis", "status": "completed", "keywords_generated": 50},
    {"step": "campaign_creation", "status": "completed", "campaign_id": "camp_gym_wear_performance"},
    {"step": "ad_group_creation", "status": "completed", "ad_groups_created": 3},
    {"step": "keyword_addition", "status": "completed", "keywords_added": 45},
    {"step": "ad_creation", "status": "completed", "ads_created": 9}
  ],
  "campaign": {
    "campaign_id": "camp_gym_wear_performance",
    "campaign_name": "Google Search - Gym Wear - Performance",
    "status": "ENABLED",
    "daily_budget": 500.0
  },
  "total_keywords": 45,
  "total_ads": 9
}
```

### 2. Tavily to Keywords (Steps 1-2)
**Endpoint**: `POST /api/v1/demo/intelligence/tavily-to-keywords`

Executes intelligence gathering and keyword analysis only.

**Parameters**:
- `client_id`: Client ID
- `topic`: Topic to research
- `max_keywords`: Maximum keywords to generate (default: 50)

**Response**:
```json
{
  "topic": "gym wear",
  "tavily_intelligence": {
    "results_count": 15,
    "answer": "Gym wear market is experiencing...",
    "query_time": 2.5
  },
  "thrad_bert_analysis": {
    "keywords_generated": 50,
    "analyzed_keywords": [
      {
        "keyword": "gym wear",
        "relevance_score": 0.9,
        "intent_score": 0.4,
        "volume_estimate": 5000,
        "competition_score": 0.6,
        "suggested_bid": 2.95,
        "category": "informational"
      }
    ]
  },
  "intelligence_summary": {
    "key_themes": ["Gym Wear Market", "Fitness Apparel Trends"],
    "trending_concepts": ["performance", "athletic", "training"],
    "consumer_insights": [
      "Consumers showing strong interest in gym wear products",
      "Price sensitivity remains a key factor"
    ],
    "market_opportunities": [
      "Target high-intent keyword: 'buy gym wear online' with low competition"
    ]
  }
}
```

### 3. Create Google Campaign (Steps 3-5)
**Endpoint**: `POST /api/v1/demo/intelligence/create-google-campaign`

Creates Google Ads campaign from provided keywords.

**Parameters**:
- `client_id`: Client ID
- `topic`: Campaign topic
- `keywords`: List of keywords (optional, will generate if not provided)
- `campaign_type`: Campaign type
- `daily_budget`: Daily budget
- `match_type`: Match type

**Response**:
```json
{
  "campaign": {
    "campaign_id": "camp_gym_wear_performance",
    "campaign_name": "Google Search - Gym Wear - Performance",
    "campaign_type": "SEARCH",
    "status": "ENABLED",
    "daily_budget": 500.0
  },
  "ad_groups": [
    {
      "ad_group_id": "adgrp_high_intent_camp_gym_wear_performance",
      "ad_group_name": "High Intent Keywords",
      "status": "ENABLED",
      "bid_amount": 2.5,
      "bid_strategy": "MANUAL_CPC"
    }
  ],
  "keywords": [
    {
      "keyword_text": "buy gym wear online",
      "match_type": "PHRASE",
      "bid_amount": 3.25,
      "status": "ENABLED"
    }
  ],
  "ads": [
    {
      "ad_name": "Search Ad 1",
      "ad_group_id": "adgrp_high_intent_camp_gym_wear_performance",
      "ad_type": "SEARCH_AD",
      "headlines": ["Gymshark Performance Wear", "Premium Fitness Apparel"],
      "descriptions": ["High-performance gym wear for serious athletes"],
      "status": "ENABLED"
    }
  ]
}
```

### 4. Campaign Performance
**Endpoint**: `GET /api/v1/demo/intelligence/campaign-performance`

Gets performance data for a Google Ads campaign.

**Parameters**:
- `client_id`: Client ID
- `campaign_id`: Google Ads campaign ID

**Response**:
```json
{
  "campaign_id": "camp_gym_wear_performance",
  "performance": {
    "impressions": 125000,
    "clicks": 3750,
    "ctr": 0.03,
    "conversions": 187,
    "cost_per_conversion": 24.0,
    "conversion_rate": 0.05,
    "cost": 4488.0,
    "revenue": 11220.0,
    "roas": 2.5
  },
  "performance_by_day": [
    {"date": "2025-06-20", "impressions": 15000, "clicks": 450, "conversions": 22}
  ]
}
```

### 5. Keyword Optimization
**Endpoint**: `POST /api/v1/demo/intelligence/optimize-keywords`

Optimizes campaign keywords using Thrad BERT analysis.

**Parameters**:
- `client_id`: Client ID
- `ad_group_id`: Google Ads ad group ID
- `topic`: Topic for new keyword generation

**Response**:
```json
{
  "ad_group_id": "adgrp_high_intent_camp_gym_wear_performance",
  "current_performance": {
    "underperforming_keywords": ["fitness clothes", "gym fashion"]
  },
  "new_keywords_from_bert": [
    "gymshark leggings",
    "athletic wear brands"
  ],
  "optimization_recommendations": [
    {
      "keyword": "fitness clothes",
      "action": "pause",
      "reason": "Low conversion rate, high cost"
    },
    {
      "keyword": "gymshark leggings",
      "action": "add",
      "reason": "High intent score from BERT analysis",
      "suggested_bid": 2.75
    }
  ]
}
```

## 🎯 Demo Flow for Gymshark

### Complete Pipeline Demo:

1. **User enters topic**: "summer training collection"
2. **System scrapes Tavily**: Gets market trends for summer fitness apparel
3. **Thrad BERT analyzes**: Generates 50 keywords with relevance/intent scores
4. **Google Ads campaign created**: "Google Search - Summer Training Collection - Performance"
5. **Ad groups created**: High Intent, Medium Intent, Broad Match groups
6. **Keywords added**: 45 keywords with calculated bids
7. **Search ads created**: 9 ads with Gymshark branding
8. **Campaign activated**: Ready to run with $500 daily budget

### Step-by-Step Demo:

**Step 1**: Research keywords
```bash
POST /intelligence/tavily-to-keywords?topic=gymshark%20summer%20collection
```

**Step 2**: Review intelligence summary
- Key themes identified
- Trending concepts extracted
- Consumer insights generated
- Top 20 keywords with scores

**Step 3**: Create campaign
```bash
POST /intelligence/create-google-campaign?topic=gymshark%20summer%20collection&daily_budget=500
```

**Step 4**: Monitor performance
```bash
GET /intelligence/campaign-performance?campaign_id=camp_gymshark_summer
```

**Step 5**: Optimize weekly
```bash
POST /intelligence/optimize-keywords?ad_group_id=adgrp_high_intent&topic=gymshark%20summer
```

## 🔐 Real API Integration

To use real Google Ads API instead of demo mode:

```python
from services.platform_integration.google_ads_manager import GoogleAdsManager

google_ads_manager = GoogleAdsManager(
    developer_token="YOUR_DEVELOPER_TOKEN",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    refresh_token="YOUR_REFRESH_TOKEN",
    customer_id="123-456-7890",
    demo_mode=False  # Enable real API calls
)
```

To use real Thrad BERT model:

```python
from services.intelligence.thrad_bert_client import ThradBERTClient

thrad_client = ThradBERTClient(
    model_path="path/to/thrad/distilbert",
    demo_mode=False  # Enable real model inference
)
```

## 📊 Keyword Scoring System

### Relevance Score (0-1)
- 0.9-1.0: Topic keyword or direct match
- 0.7-0.9: Contains topic words
- 0.5-0.7: Related to topic
- <0.5: Low relevance

### Intent Score (0-1)
- 0.9-1.0: Transactional (buy, shop, order)
- 0.7-0.9: Commercial (best, top, review)
- 0.4-0.7: Informational
- <0.4: Navigational

### Volume Estimate
- Calculated based on relevance, length, and intent
- Longer keywords = higher specificity
- Transactional intent = higher volume

### Competition Score (0-1)
- Longer keywords = lower competition
- Calculated as: 1.0 - (word_count * 0.15)
- Minimum 0.2

### Suggested Bid
- Base bid: $1.50
- Intent multiplier: +$2.00 for transactional
- Competition multiplier: +$1.00 for high competition
- Length multiplier: Up to +50% for longer phrases

## 🎨 Creative Generation

The system automatically generates:

**Headlines** (up to 30 chars each):
- Gymshark Performance Wear
- Premium Fitness Apparel
- Train Like a Champion

**Descriptions** (up to 90 chars each):
- High-performance gym wear for serious athletes
- Shop the latest fitness apparel and accessories

**Final URL**: https://www.gymshark.com

## 📈 Performance Metrics Tracked

- Impressions
- Clicks
- CTR (Click-through rate)
- Conversions
- Cost per conversion
- Conversion rate
- Total cost
- Revenue
- ROAS (Return on ad spend)

## 🔄 Optimization Loop

1. **Weekly performance check**: Get campaign performance
2. **Underperforming keyword identification**: Keywords with low conversion/high cost
3. **New keyword generation**: Thrad BERT analyzes fresh intelligence
4. **Recommendation generation**: Pause/add keywords based on analysis
5. **Bid adjustments**: Adjust bids based on performance
6. **Creative refresh**: Update ads if saturation high (from adstock analysis)

This creates a continuous intelligence → analysis → optimization → activation loop!