# SIGNAL Platform - Frontend Design Specification (Backend-Aligned)

**Version**: 2.0
**Date**: 2025-11-28
**Based on**: Complete Backend API Review

---

## Overview

This frontend specification is directly aligned with the backend API routes, business logic, and data structures. Every UI component maps to specific backend endpoints and reflects the actual business logic implemented.

---

## API-to-UI Mapping Summary

| Backend Route | UI Component | Data Model |
|---------------|---------------|------------|
| `/terminal/agent-logs` | Agent Execution Log | AgentLog |
| `/terminal/campaign-signals` | Agent Signals Panel | CampaignSignal |
| `/terminal/channel-metrics` | Campaign P&L Panel | ChannelMetric |
| `/planning/campaign-keyword-logs` | Campaign Keyword Logs | KeywordAddLog |
| `/planning/complete-planning-with-keywords` | Tavily Research Panel | ResearchResult |
| `/chat/chat` | AI Chat Interface | ChatRequest/Response |
| `/intelligence/gymshark-*` | Intelligence Panel | TavilyResearchResult |

---

## Page 1: Bloomberg Terminal Dashboard (Backend-Aligned)

### API Endpoints Used
- `GET /terminal/agent-logs` - Real-time agent execution logs
- `GET /terminal/campaign-signals` - BUY/HOLD/STOP signals
- `GET /terminal/channel-metrics` - Platform performance metrics
- `GET /terminal/header-stats` - Overall stats
- `GET /terminal/full-dashboard` - Complete dashboard data

### Backend Business Logic
**Agent Log Generation** (from `services/common/agent_logger.py`):
```python
def generate_agent_logs():
    """Generate agent logs for Bloomberg Terminal."""
    campaigns = [
        "Summer Training Collection Launch",
        "Performance Training Gear",
        "TikTok Fitness Challenge"
    ]
    
    actions = ["BUY", "HOLD", "STOP"]
    agents = ["THOMPSON_ALLOCATOR", "BID_STRATEGY", "CREATIVE_OPT"]
    
    # Returns logs with:
    # - timestamp
    # - agent name
    # - action (BUY/HOLD/STOP)
    # - campaign name
    # - channel
    # - amount in GBP
    # - confidence score
```

**Signal Logic**:
- BUY: Confidence > 75%, spend > £1,000
- HOLD: Confidence 50-75%, spend £500-1,000
- STOP: Confidence < 50% or spend < £500

### UI Layout (Backend-Aligned)
```
┌─────────────────────────────────────────────────────────────────┐
│  SIGNAL TERMINAL                    GYMSHARK │  [Refresh: 5s] │
├─────────────────────────────────────────────────────────────────┤
│  Header Stats (from /terminal/header-stats)                    │
│  ROAS: 3.25 (+55%)  CPL: £28 (-20%)  Leads: 1,120 (+40%)      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Campaign Signals (from /terminal/campaign-signals)            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ ⚡ BUY          │  │ ⏸️ HOLD         │  │ 🛑 STOP         │ │
│  │ Summer Training │  │ Performance Gear│  │ Old Campaign    │ │
│  │ £2,500 (85%)    │  │ £1,800 (72%)    │  │ £0 (0%)         │ │
│  │ ROAS: 4.2       │  │ ROAS: 3.1       │  │ ROAS: 1.8       │ │
│  │ Channel: Meta   │  │ Channel: Google  │  │ Channel: TikTok  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  Channel Metrics (from /terminal/channel-metrics)              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Channel    Spend      Leads    CPA     Trend              │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Meta       £12,500    450      £28     ↑ +12%             │ │
│  │ Google     £10,800    520      £21     ↑ +8%              │ │
│  │ TikTok     £8,200     380      £22     ↓ -5%              │ │
│  │ Microsoft  £7,500     280      £27     ↑ +3%              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Agent Execution Log (from /terminal/agent-logs)               │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 21:04:19 [THOMPSON_ALLOCATOR] BUY Summer Training £2,500   │ │
│  │   Campaign: Summer Training Collection Launch               │ │
│  │   Channel: Meta  Confidence: 85%  ROAS: 4.2                │ │
│  │                                                              │ │
│  │ 21:03:45 [BID_STRATEGY] Optimized bid for gymshark leggs  │ │
│  │   Campaign: Performance Training Gear                        │ │
│  │   Channel: Google  Confidence: 78%  Old: £2.20 → New: £2.75 │ │
│  │                                                              │ │
│  │ 21:02:12 [CREATIVE_OPT] Selected video creative variant B  │ │
│  │   Campaign: TikTok Fitness Challenge                        │ │
│  │   Channel: TikTok  Confidence: 82%  Lift: +15%              │ │
│  │                                                              │ │
│  │ 21:01:33 [MARKET_ANALYSIS] Detected +15% trending interest │ │
│  │   Source: Tavily  Topic: Gymshark seamless leggings         │ │
│  │                                                              │ │
│  │ 21:00:45 [ORCHESTRATION] Coordinated workflow update       │ │
│  │   Task: Media Planning  Agents: 5  Success: 100%            │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Real-time Updates
- **WebSocket**: Subscribe to `/ws/terminal/updates`
- **Polling fallback**: Every 5 seconds
- **Data refresh**: Auto-refresh agent logs every 10 seconds

---

## Page 2: Media Planning Dashboard (Backend-Aligned)

### API Endpoints Used
- `POST /planning/complete-planning-with-keywords` - Complete research + keyword logging
- `GET /planning/campaign-keyword-logs` - Get logged keywords
- `GET /intelligence/gymshark-reddit` - Reddit scraping
- `GET /intelligence/gymshark-google-keywords` - Google keywords
- `GET /intelligence/gymshark-thrad-inputs` - Thrad BERT inputs

### Backend Business Logic
**Keyword Logging with DisBERT** (from `services/media_planning/campaign_keyword_logger.py`):
```python
def log_keywords_from_research(
    google_keywords: List[Dict],
    source: str = "tavily",
    model_used: Optional[str] = None  # "thrad_disbert"
) -> List[KeywordAddLog]:
    """
    Log keywords with model specification.
    
    Log format:
    - timestamp
    - campaign_name: "GYMSHARK_PPC_GENERIC_2026"
    - keyword, match_type, bid_amount
    - source (tavily, manual, bert, thrad)
    - confidence, intent, category
    - model_used: "thrad_disbert" (if used)
    - thrad_data: Full conversation context
    """
```

**DisBERT Classification** (from `services/intelligence/disbert_thrad_classification.py`):
```python
def classify_query_with_disbert(query: str) -> DisBERTThradClassification:
    """
    Classify query into A-M categories.
    
    H = Purchasable Products (high value for ads)
    E = General Guidance (educational)
    L = Other
    """
```

### UI Layout (Backend-Aligned)
```
┌─────────────────────────────────────────────────────────────────┐
│  MEDIA PLANNING                                    [Auto-refresh] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  TAVILY RESEARCH (POST /planning/complete-planning)       │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  Query: [Gymshark fitness apparel]  [🔍 Research]          │ │
│  │  Use DisBERT: [✓]  Max Results: [10]                     │ │
│  │                                                              │ │
│  │  Research Summary:                                          │ │
│  │  Reddit Posts: 15  SEO Keywords: 45  Google Kws: 30        │ │
│  │  Thrad Inputs: 25  Content Ideas: 12                       │ │
│  │                                                              │ │
│  │  Top Reddit Insights:                                       │ │
│  │  • "Gymshark seamless leggings best for summer" (245 up)   │ │
│  │  • "Summer collection worth the hype?" (178 up)            │ │
│  │                                                              │ │
│  │  Google Keywords for Bidding:                               │ │
│  │  Keyword              Match  Bid    Intent   Category      │ │
│  │  gymshark leggings    phrase £2.75  trans    H             │ │
│  │  buy gymshark online  exact  £3.50  trans    H             │ │
│  │  gym wear women       broad  £2.20  info     E             │ │
│  │  Model: thrad_disbert ✓                                      │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  CAMPAIGN KEYWORD LOGS (GET /planning/campaign-keyword-logs)│ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  Campaign: GYMSHARK_PPC_GENERIC_2026  Model: thrad_disbert │ │
│  │  Filter by Source: [All ▼]  [Tavily] [BERT] [Manual]      │ │
│  │                                                              │ │
│  │  Keyword              Match  Bid    Source    Logged        │ │
│  │  gymshark leggings    phrase £2.75  tavily    2 min ago    │ │
│  │  buy gym clothes      exact  £3.20  tavily    2 min ago    │ │
│  │  fitness workout      broad  £1.85  bert      5 min ago    │ │
│  │  seamless leggings    phrase £2.50  manual    10 min ago   │ │
│  │                                                              │ │
│  │  [📊 View Thrad Data]  [📤 Export Logs]  [🔄 Refresh]    │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Thrad Data Modal (Backend-Aligned)
```javascript
// When clicking "View Thrad Data"
{
  "user_id": "user_123",
  "chat_id": "chat_456",
  "messages": [
    {
      "role": "user",
      "content": "Looking for gymshark leggings",
      "timestamp": "2025-11-23T10:00:00Z"
    },
    {
      "role": "assistant",
      "content": "What's your budget?",
      "timestamp": "2025-11-23T10:00:15Z"
    }
  ],
  "summary": "User is interested in gymshark leggings",
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
  "ad_formats": ["sponsored_message", "banner"],
  "model_used": "thrad_disbert"
}
```

---

## Page 3: Agent Management (Backend-Aligned)

### API Endpoints Used
- `GET /terminal/agent-logs` - Agent execution history
- `GET /planning/channel-mappings` - Channel allocation
- Database: `agent_execution_history` table

### Backend Business Logic
**Agent Execution History** (from `shared/models/demo_models.py`):
```python
class AgentExecutionHistory(Base):
    """Track agent execution for audit."""
    
    agent_name: str  # bid_strategy_agent, content_brief_agent, etc.
    agent_type: str  # bid_strategy, content_brief, etc.
    action: str  # optimize_bid, generate_content, etc.
    input_data: dict
    output_data: dict
    execution_time_ms: int
    tokens_used: int
    cost_usd: Decimal
    success: bool
    error_message: Optional[str]
    execution_date: datetime
```

### UI Layout (Backend-Aligned)
```
┌─────────────────────────────────────────────────────────────────┐
│  AGENT MANAGEMENT                                  [Last 30 Days ▼]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ BID STRATEGY    │  │ CONTENT BRIEF  │  │ CREATIVE OPT    │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ Status: ✅ Active│  │ Status: ✅ Active│  │ Status: ✅ Active│ │
│  │ Executions: 750  │  │ Executions: 720  │  │ Executions: 680  │ │
│  │ Success: 92%     │  │ Success: 95%     │  │ Success: 89%     │ │
│  │ Latency: 450ms  │  │ Latency: 620ms  │  │ Latency: 380ms  │ │
│  │ Tokens: 75,000   │  │ Tokens: 82,000   │  │ Tokens: 68,000   │ │
│  │ Cost: £0.75      │  │ Cost: £0.82      │  │ Cost: £0.68      │ │
│  │                 │  │                 │  │                 │ │
│  │ [View Policy]   │  │ [View Policy]   │  │ [View Policy]   │ │
│  │ [View History]  │  │ [View History]  │  │ [View History]  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐                       │
│  │ MARKET ANALYSIS │  │ ORCHESTRATION   │                       │
│  ├─────────────────┤  ├─────────────────┤                       │
│  │ Status: ✅ Active│  │ Status: ✅ Active│                       │
│  │ Executions: 810  │  │ Executions: 890  │                       │
│  │ Success: 94%     │  │ Success: 97%     │                       │
│  │ Latency: 520ms  │  │ Latency: 890ms  │                       │
│  │ Tokens: 95,000   │  │ Tokens: 110,000  │                       │
│  │ Cost: £0.95      │  │ Cost: £1.10      │                       │
│  │                 │  │                 │                       │
│  │ [View Policy]   │  │ [View Policy]   │                       │
│  │ [View History]  │  │ [View History]  │                       │
│  └─────────────────┘  └─────────────────┘                       │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  RECENT EXECUTION HISTORY (Last 20)                        │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ 21:04:19 [BID_STRATEGY] optimize_bid                      │ │
│  │   Input: {"keyword": "gymshark leggings", "current_bid": 2.20}│ │
│  │   Output: {"recommended_bid": 2.75, "confidence": 0.85}      │ │
│  │   Success: ✅  Time: 450ms  Tokens: 150  Cost: £0.0015       │ │
│  │                                                              │ │
│  │ 21:03:45 [CONTENT_BRIEF] generate_content                   │ │
│  │   Input: {"gap_topic": "seamless leggings", "gap_score": 0.85}│ │
│  │   Output: {"brief": "...", "confidence": 0.92}               │ │
│  │   Success: ✅  Time: 620ms  Tokens: 280  Cost: £0.0028       │ │
│  │                                                              │ │
│  │ 21:02:12 [CREATIVE_OPT] analyze_creative                     │ │
│  │   Input: {"creative_id": "cr_123", "performance": {...}}       │ │
│  │   Output: {"score": 75, "suggestions": [...]}                │ │
│  │   Success: ✅  Time: 380ms  Tokens: 120  Cost: £0.0012       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Page 4: LLM Chat Interface (Backend-Aligned)

### API Endpoints Used
- `GET /chat/agents` - List available agents
- `GET /chat/models` - List available models
- `POST /chat/chat` - Send message
- `GET /chat/conversations` - List conversations
- `POST /chat/conversations/{id}/agent` - Switch agent
- `POST /chat/conversations/{id}/model` - Switch model

### Backend Business Logic
**Available Agents** (from `api/routes/chat.py`):
```python
AGENTS = {
    "general": {"name": "General", "description": "General purpose assistant"},
    "bid_strategy": {"name": "Bid Strategy", "description": "Bidding strategy optimization"},
    "content_brief": {"name": "Content Brief", "description": "Content brief generation"},
    "creative_optimization": {"name": "Creative Optimization", "description": "Creative performance optimization"},
    "market_analysis": {"name": "Market Analysis", "description": "Market intelligence and insights"},
    "orchestration": {"name": "Orchestration", "description": "Multi-agent coordination"}
}
```

**Available Models**:
```python
MODELS = {
    "gpt-4": {"name": "GPT-4", "description": "Most capable model"},
    "gpt-4-turbo": {"name": "GPT-4 Turbo", "description": "Faster, more cost-effective"},
    "gpt-3.5-turbo": {"name": "GPT-3.5 Turbo", "description": "Fastest, most cost-effective"},
    "gpt-4o": {"name": "GPT-4 Omni", "description": "Latest multimodal model"}
}
```

### UI Layout (Backend-Aligned)
```
┌─────────────────────────────────────────────────────────────────┐
│  AI CHAT                                         [GPT-4 ▼]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Select Agent:                                              │ │
│  │  [🤖 General] [💰 Bid Strategy] [📝 Content Brief]         │ │
│  │  [🎨 Creative Opt] [📊 Market Analysis] [🎯 Orchestration] │ │
│  │                                                              │ │
│  │  Current Agent: Bid Strategy  Model: GPT-4                 │ │
│  │  [Switch Agent]  [Switch Model]  [New Conversation]        │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  💬 Conversation History (chat_456)                         │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  You: What's the optimal bid for gymshark leggings?         │ │
│  │  21:04:19  🤖 Bid Strategy (GPT-4):                        │ │
│  │     Based on current market conditions, I recommend a bid   │ │
│  │     of £2.75 for phrase match. The competition is moderate  │ │
│  │     and conversion rate is 3.5%.                           │ │
│  │     Confidence: 0.85  Tokens: 150  Cost: £0.0015           │ │
│  │                                                              │ │
│  │  You: Generate content brief for summer collection         │ │
│  │  21:03:45  🤝 Content Brief (GPT-4):                        │ │
│  │     Creating brief for Summer 2025...                       │ │
│  │     Topic: Seamless Leggings Launch                          │ │
│  │     Angle: Performance fabric meets summer comfort          │ │
│  │     Hook: "Experience the leggings that move with you"      │ │
│  │     Confidence: 0.92  Tokens: 280  Cost: £0.0028           │ │
│  │                                                              │ │
│  │  You: How are campaigns performing?                         │ │
│  │  21:02:12  📊 Market Analysis (GPT-4):                      │ │
│  │     Overall ROAS is 3.25, up 55% from baseline. Top         │ │
│  │     performer is Summer Training with ROAS of 4.2.          │ │
│  │     Confidence: 0.88  Tokens: 195  Cost: £0.0019           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Type your message...]                                    [Send] │
└─────────────────────────────────────────────────────────────────┘
```

---

## Page 5: Analytics Dashboard (Backend-Aligned)

### API Endpoints Used
- Database: `campaign_performance` table (12 months historical)
- Database: `model_performance` table (prediction accuracy)
- Database: `keyword_performance` table (30 days)
- Database: `ab_test_campaigns` and `ab_test_results` tables
- Database: `content_performance_by_channel` table

### Backend Data Structure
**Historical Campaign Performance**:
```python
# From scripts/comprehensive_demo_data.py
# 12 campaigns across seasons
# Weekly performance records
# Seasonal trends

Campaign Performance:
- Summer 2024: ROAS 2.1
- Fall 2024: ROAS 2.8
- Winter 2025: ROAS 3.1
- Spring 2025: ROAS 3.8
- Current: ROAS 4.2
```

**Model Performance**:
```python
# From shared/models/demo_models.py
# 1,200 records over 6 months
# Tracks: predicted_value vs actual_value
# Calculates: absolute_error, percentage_error, is_accurate
```

**A/B Tests**:
```python
# 3 tests: 2 completed, 1 running
# Creative Test: Winner = Video (92% confidence)
# Bid Strategy Test: Winner = Automated (88% confidence)
# Audience Test: Running (7 days in)
```

### UI Layout (Backend-Aligned)
```
┌─────────────────────────────────────────────────────────────────┐
│  ANALYTICS                                      [Last 12 Months ▼]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  HISTORICAL CAMPAIGN PERFORMANCE                            │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  [📈 ROAS Trend Chart - 12 Months Data]                    │ │
│  │  4.5 ┤     ╭────╮                                           │ │
│  │  4.0 ┤   ╭─╯    ╰─╮                                         │ │
│  │  3.5 ┤ ╭─╯         ╰─╮                                       │ │
│  │  3.0 ┤─╯             ╰───╮                                   │ │
│  │  2.5 ┤                    ╰─╮                                 │ │
│  │  2.0 ┤                       ╰───╮                           │ │
│  │      └─────────────────────────────╮─────────────────────   │ │
│  │        Jun Jul Aug Sep Oct Nov Dec Jan Feb Mar Apr May      │ │
│  │                                                              │ │
│  │  Seasonal Breakdown:                                         │ │
│  │  Summer 2024: 2.1  Fall 2024: 2.8  Winter 2025: 3.1        │ │
│  │  Spring 2025: 3.8  Current: 4.2 (+55% vs baseline)          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ MODEL ACCURACY  │  │ KEYWORD PERF   │  │ A/B TESTS       │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ Bid Strategy:   │  │ Top Keywords:   │  │ Creative Test:  │ │
│  │ 92% accuracy    │  │ gymshark leggs  │  │ Winner: Video   │ │
│  │ (1,200 preds)   │  │ ROAS: 4.5      │  │ Confidence: 92% │ │
│  │                 │  │ (30 days data)  │  │ Duration: 14d   │ │
│  │ Keyword Class:  │  │ buy gym clothes │  │                 │ │
│  │ 88% accuracy    │  │ ROAS: 3.8      │  │ Bid Test:       │ │
│  │                 │  │                 │  │ Winner: Auto    │ │
│  │ Creative Opt:   │  │ fitness workout │  │ Confidence: 88% │ │
│  │ 85% accuracy    │  │ ROAS: 2.9      │  │ Duration: 14d   │ │
│  │                 │  │                 │  │                 │ │
│  │ [View Details]  │  │ [View Details]  │  │ [View Details]  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Page 6: Keyword Intelligence (Backend-Aligned)

### API Endpoints Used
- Database: `keyword_performance` table (1,500 records, 30 days)
- Service: `services/intelligence/disbert_thrad_classification.py`
- Service: `services/media_planning/campaign_keyword_logger.py`

### Backend Business Logic
**DisBERT Classification**:
```python
# From services/intelligence/disbert_thrad_classification.py
classification = integrator.classify_query_with_disbert("buy gymshark online")
# Returns: DisBERTThradClassification.H (Purchasable Products)

# Get keyword strategy
strategy = integrator.get_google_ads_keywords_for_classification(classification)
# Returns: use_as_keywords=True, commercial_intent=0.95, etc.
```

**Keyword Performance**:
```python
# From shared/models/demo_models.py
class KeywordPerformance(Base):
    keyword: str
    match_type: str
    impressions: int
    clicks: int
    conversions: int
    spend: Decimal
    revenue: Decimal
    ctr: Decimal
    cpa: Decimal
    roas: Decimal
    current_bid: Decimal
    bid_suggestion: Decimal
    category: str  # H, G, A, E, L, M
    intent: str  # informational, transactional
    performance_date: date
```

### UI Layout (Backend-Aligned)
```
┌─────────────────────────────────────────────────────────────────┐
│  KEYWORD INTELLIGENCE                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  DISBERT CLASSIFICATION                                      │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  Query: [gymshark leggings]  [🔍 Classify]                  │ │
│  │                                                              │ │
│  │  Category: H (Purchasable Products)                          │ │
│  │  Use as Keywords: ✅ Yes                                     │ │
│  │  Commercial Intent: 0.95                                    │ │
│  │  Should Ingest: ✅ Yes (Priority 8)                          │ │
│  │                                                              │ │
│  │  Keyword Strategy:                                           │ │
│  │  • Use as keywords: gymshark leggings, seamless leggings    │ │
│  │  • Suggested bid: £2.75                                     │ │
│  │  • Match types: phrase, exact                               │ │
│  │  • Commercial intent: 0.95                                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  KEYWORD PERFORMANCE (30 Days - 1,500 Records)               │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  Keyword              Match  Impressions  Clicks  Conv  CPA  ROAS│ │
│  │  gymshark leggings    phrase 125,000      3,750   150   £18  4.2│ │
│  │  buy gym clothes      exact   98,000      2,940   125   £20  3.8│ │
│  │  fitness workout      broad   85,000      2,550    95   £22  3.4│ │
│  │  seamless leggings    phrase 110,000      3,300   140   £19  4.0│ │
│  │  gym wear women       broad  95,000      2,850   115   £21  3.6│ │
│  │                                                              │ │
│  │  Filter by Category: [All ▼] [H] [E] [L]                     │ │
│  │  Filter by Intent: [All ▼] [Transactional] [Informational]   │ │
│  │  Sort by: [ROAS ▼] [CPA] [Clicks] [Conversions]              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  THRAD DATA (from Keyword Log)                              │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  User: user_123  Chat: chat_456                            │ │
│  │  Summary: User interested in gymshark leggings              │ │
│  │  Model: thrad_disbert                                       │ │
│  │  Config: ad_offset=3, max_freq=5, experiment=variant_a      │ │
│  │  Messages: 4  Turns: 4  Ad Formats: sponsored, banner      │ │
│  │  User Metadata: age_range=25-34, gender=female, location=UK  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### Agent Signal Generation Flow
```
Database (campaign_performance)
    ↓
Agent Logger (generate_agent_logs)
    ↓
API: GET /terminal/agent-logs
    ↓
UI: Agent Execution Log Panel
```

### Keyword Logging Flow
```
Tavily Research
    ↓
Google Keywords Extraction
    ↓
DisBERT Classification
    ↓
Campaign Keyword Logger (log_keywords_from_research)
    ↓
Database (keyword_logs, keyword_performance)
    ↓
API: GET /planning/campaign-keyword-logs
    ↓
UI: Campaign Keyword Logs Panel
```

### Chat Flow
```
User Input
    ↓
API: POST /chat/chat
    ↓
Agent Selection (bid_strategy, content_brief, etc.)
    ↓
Model Selection (GPT-4, GPT-4 Turbo, etc.)
    ↓
OpenAI API Call
    ↓
Response with tokens_used, cost_usd
    ↓
UI: Chat Message Bubble with metadata
```

---

## Real-time Data Updates

### WebSocket Endpoints
- `/ws/terminal/updates` - Agent logs, signals, metrics
- `/ws/keyword-updates` - Keyword performance updates
- `/ws/chat-updates` - Chat message updates

### Polling Fallbacks
- Terminal: Every 5 seconds
- Keyword logs: Every 10 seconds
- Analytics: Every 30 seconds
- Chat: Every 2 seconds (when active)

---

## Error Handling

### API Error Responses
```javascript
// Example: Tavily API key not configured
{
  "error": "TAVILY_API_KEY not configured",
  "code": 400,
  "message": "Configure TAVILY_API_KEY in .env.local"
}
```

### UI Error States
- **Loading**: Skeleton screens
- **Error**: Error modal with retry button
- **Empty**: Empty state with call-to-action
- **Offline**: Offline indicator with cached data

---

## Performance Optimization

### Data Caching Strategy
- **Agent Logs**: Cache for 10 seconds
- **Campaign Signals**: Cache for 5 seconds
- **Historical Data**: Cache for 1 hour
- **Keyword Performance**: Cache for 30 seconds

### Lazy Loading
- **Chat History**: Load 50 messages, load more on scroll
- **Agent History**: Load 20 records, load more on scroll
- **Keyword Performance**: Load 50 records, paginate

---

## Conclusion

This frontend specification is 100% aligned with the backend implementation:
- ✅ Every UI component maps to specific API endpoints
- ✅ Business logic from backend is accurately reflected
- ✅ Data structures match backend models
- ✅ Real-time updates match backend capabilities
- ✅ Error handling matches backend responses
- ✅ Performance optimization matches backend constraints

The UI will accurately represent what's happening in the backend with no disconnect between displayed data and actual business logic.