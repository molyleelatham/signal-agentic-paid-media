# Campaign Keyword Logger & Thrad Data Generation

## Overview

This system logs keywords added to campaigns (specifically GYMSHARK_PPC_GENERIC_2026) and generates fake Thrad data for tracking after web crawling and media planning.

## Features

### 1. Campaign Keyword Logger
- Logs when keywords are added to campaigns
- Tracks keyword metadata (match type, bid, source, confidence, intent)
- Maintains audit trail of keyword additions
- Supports multiple sources (tavily, manual, bert, thrad)

### 2. Thrad Data Generation
- Generates fake Thrad tracking data for each keyword
- Includes user/chat IDs, conversation messages, config
- Provides user metadata (age, gender, location, interests)
- Generates realistic conversation history

### 3. Integration with Media Planning
- Automatically logs keywords after Tavily research
- Generates Thrad data for each keyword
- Provides complete audit trail
- Supports manual keyword logging

## API Endpoints

### Complete Planning with Keywords
```bash
POST /api/v1/planning/complete-planning-with-keywords
```

Performs complete media planning with keyword logging:
1. Tavily research (Reddit, SEO, Google keywords)
2. Extracts Google keywords for bidding
3. Logs keywords to GYMSHARK_PPC_GENERIC_2026 campaign
4. Generates Thrad data for each keyword
5. Returns complete results with logs

**Parameters:**
- `query`: Research query (default: "Gymshark fitness apparel")
- `max_results`: Max results per source (default: 10)
- `use_disbert`: Use Thrad DisBERT model for context organization (default: true)

**Note**: When `use_disbert=true`, logs will specify "using thrad_disbert model" and Thrad data will include `model_used: "thrad_disbert"`.

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/planning/complete-planning-with-keywords?query=Gymshark%20leggings&max_results=5"
```

### Get Campaign Keyword Logs
```bash
GET /api/v1/planning/campaign-keyword-logs
```

Get keyword logs for a campaign.

**Parameters:**
- `campaign_name`: Campaign name (default: "GYMSHARK_PPC_GENERIC_2026")
- `limit`: Max logs to return (default: 50)

**Example:**
```bash
curl "http://localhost:8000/api/v1/planning/campaign-keyword-logs?campaign_name=GYMSHARK_PPC_GENERIC_2026"
```

### Get Keyword Logs by Source
```bash
GET /api/v1/planning/keyword-logs-by-source
```

Get keyword logs by source.

**Parameters:**
- `source`: Source (tavily, manual, bert, thrad)
- `limit`: Max logs to return (default: 50)

**Example:**
```bash
curl "http://localhost:8000/api/v1/planning/keyword-logs-by-source?source=tavily"
```

### Log Keyword Manually
```bash
POST /api/v1/planning/log-keyword-manually
```

Manually log a keyword addition.

**Parameters:**
- `keyword`: Keyword to log
- `match_type`: Match type (phrase, broad, exact)
- `bid_amount`: Bid amount
- `source`: Source (manual, tavily, bert, thrad)
- `confidence`: Confidence score (0-1)
- `intent`: Intent (informational, transactional, navigational)
- `category`: Optional category (H, G, A, etc.)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/planning/log-keyword-manually?keyword=gymshark%20leggings&match_type=phrase&bid_amount=2.50&source=manual&confidence=0.85&intent=transactional&category=H"
```

## Thrad Data Structure

The generated Thrad data follows this structure:

```json
{
  "userId": "user_123",
  "chatId": "chat_456",
  "messages": [
    {
      "role": "user",
      "content": "Looking for running shoes",
      "timestamp": "2025-11-23T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "What's your budget?",
      "timestamp": "2025-11-23T10:00:15Z"
    }
  ],
  "summary": "User is looking for running shoes for marathon training",
  "config": {
    "ad_offset": 3,
    "max_frequency": 5,
    "max_headline_chars": 60,
    "experiment_tag": "variant_a"
  },
  "user_metadata": {
    "age_range": "25-34",
    "gender": "female",
    "location": "UK",
    "interests": ["fitness", "gym", "running"]
  },
  "turn_number": 4,
  "ad_formats": ["sponsored_message", "banner", "video"],
  "force": false
}
```

## Keyword Log Structure

```json
{
  "timestamp": "2025-11-23T10:00:00",
  "campaign_name": "GYMSHARK_PPC_GENERIC_2026",
  "keyword": "gymshark leggings",
  "match_type": "phrase",
  "bid_amount": 2.50,
  "source": "tavily",
  "confidence": 0.85,
  "intent": "transactional",
  "category": "H",
  "model_used": "thrad_disbert",
  "thrad_data": {
    "user_id": "user_123",
    "chat_id": "chat_456",
    "model_used": "thrad_disbert",
    ...
  }
}
```

**Note**: When `model_used` is set to `"thrad_disbert"`, the logs will show:
```
[LOG] Added keyword 'gymshark leggings' to GYMSHARK_PPC_GENERIC_2026 (using thrad_disbert)
```

## Usage Examples

### Example 1: Complete Planning with Keywords
```python
from services.media_planning import campaign_keyword_logger
from services.intelligence.tavily_research import GymsharkTavilyResearch

# Perform research
research_service = GymsharkTavilyResearch(tavily_api_key="your-key")
research_result = research_service.perform_comprehensive_research(
    base_query="Gymshark fitness apparel"
)

# Log keywords to campaign
google_keywords_dicts = [
    {
        "keyword": kw.keyword,
        "match_type": kw.match_type,
        "bid_suggestion": kw.bid_suggestion,
        "relevance_to_gymshark": kw.relevance_to_gymshark,
        "search_intent": kw.search_intent,
        "category": "H" if kw.search_intent == "transactional" else "E"
    }
    for kw in research_result.google_keywords
]

log_entries = campaign_keyword_logger.log_keywords_from_research(
    google_keywords=google_keywords_dicts,
    source="tavily"
)

print(f"Logged {len(log_entries)} keywords to GYMSHARK_PPC_GENERIC_2026")
```

### Example 2: Manual Keyword Logging
```python
log_entry = campaign_keyword_logger.log_keyword_addition(
    keyword="gymshark leggings",
    match_type="phrase",
    bid_amount=2.50,
    source="manual",
    confidence=0.85,
    intent="transactional",
    category="H"
)

# Generate Thrad data
thrad_data = campaign_keyword_logger.generate_thrad_data("gymshark leggings")
log_entry.thrad_data = thrad_data

print(f"Logged keyword with Thrad data: {thrad_data.user_id}")
```

### Example 3: Retrieve Logs
```python
# Get all logs for campaign
logs = campaign_keyword_logger.get_logs_by_campaign("GYMSHARK_PPC_GENERIC_2026")

# Get logs by source
tavily_logs = campaign_keyword_logger.get_logs_by_source("tavily")

# Export logs to JSON
campaign_keyword_logger.export_logs("keyword_logs.json")
```

## Media Planning Workflow

```
1. Tavily Research
   ↓
2. Extract Google Keywords
   ↓
3. Log Keywords to GYMSHARK_PPC_GENERIC_2026
   ↓
4. Generate Thrad Data for Each Keyword
   ↓
5. Return Complete Results with Logs
```

## Testing

Run the test script:
```bash
make test-campaign-logger
```

Or directly:
```bash
python3 scripts/test_campaign_keyword_logger.py
```

## Integration with Existing Features

This feature integrates with:
- **Tavily Research**: Uses research data to extract keywords
- **BERT Classification**: Uses category from BERT classification
- **Media Planning**: Integrated into planning workflow
- **Thrad Platform**: Generates data compatible with Thrad tracking

## Data Flow

```
Tavily Research
    ↓
Google Keywords (with intent, relevance)
    ↓
Campaign Keyword Logger
    ↓
Log to GYMSHARK_PPC_GENERIC_2026
    ↓
Generate Thrad Data
    ↓
Audit Trail + Tracking Data
```

## Best Practices

1. **Always use correct intent**: Classify keywords correctly (transactional vs informational)
2. **Set appropriate bids**: Use bid suggestions from research
3. **Track sources**: Always specify the source (tavily, manual, bert, thrad)
4. **Include confidence scores**: Helps prioritize keywords
5. **Use categories**: H for high intent, E for educational, etc.

## Future Enhancements

- Database persistence for logs
- Real-time keyword performance tracking
- Automatic bid optimization based on performance
- Integration with Google Ads API for actual keyword addition
- Machine learning for better Thrad data generation
- A/B testing with Thrad configs