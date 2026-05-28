# SIGNAL Platform - API and Agent Technical Specification

**Purpose**: Technical specification of API endpoints and agent inputs/outputs for frontend integration
**Target Audience**: Frontend Development Team
**Format**: Technical specification with JSON schemas and data structures

---

## API Endpoint Specifications

### Planning Flow Endpoints

#### GET `/api/v1/planning/funnel-allocation`

**Purpose**: Retrieve current marketing funnel allocation

**Input Parameters**:
```typescript
{
  client_id: string  // Required: Client identifier
}
```

**Output Schema**:
```typescript
{
  funnel_allocation: {
    awareness: number,      // Percentage (0-100)
    consideration: number,  // Percentage (0-100)
    performance: number     // Percentage (0-100)
  },
  channel_breakdown: {
    [channel_name: string]: {
      funnel_stage: string,           // "awareness" | "consideration" | "performance"
      typical_cpa: number,            // Cost per acquisition
      typical_conversion_rate: number, // Conversion rate (0-1)
      default_weight: number          // Allocation weight
    }
  },
  total_channels: number,
  risk_score: number,
  description: string
}
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Invalid client_id
- `404`: Client not found

---

#### POST `/api/v1/planning/funnel-allocation`

**Purpose**: Update funnel allocation percentages

**Input Parameters**:
```typescript
{
  client_id: string,      // Required: Client identifier
  awareness: number,      // Required: Percentage (0-100)
  consideration: number,  // Required: Percentage (0-100)
  performance: number     // Required: Percentage (0-100)
}
```

**Validation Rules**:
- All percentages must be numbers
- Sum of percentages must equal 100 (±1% tolerance)
- All percentages must be between 0 and 100

**Output Schema**:
```typescript
{
  updated_allocation: {
    awareness: number,
    consideration: number,
    performance: number
  },
  scenario_result: {
    expected_leads: number,
    expected_revenue: number,
    risk_score: number,
    confidence: number
  },
  channel_allocations: {
    [channel_name: string]: number  // Budget amount
  },
  recommendations: string[]
}
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Invalid allocation (doesn't sum to 100)
- `404`: Client not found

---

#### GET `/api/v1/planning/recommendations`

**Purpose**: Get AI-powered allocation recommendations

**Input Parameters**:
```typescript
{
  client_id: string,  // Required: Client identifier
  goal: string        // Optional: Business goal (default: "customer_acquisition")
}
```

**Goal Enum Values**:
- `customer_acquisition`
- `brand_awareness`
- `retention`
- `revenue_growth`

**Output Schema**:
```typescript
{
  business_goal: string,
  recommended_allocation: {
    awareness: number,
    consideration: number,
    performance: number
  },
  recommended_channels: string[],  // Channel names
  reasoning: string,
  expected_outcomes: {
    expected_leads: number,
    expected_roas: number,
    confidence: number
  },
  risk_assessment: {
    risk_level: string,
    factors: string[]
  },
  confidence: number,  // 0-1
  alternatives: Array<{
    allocation: { awareness: number, consideration: number, performance: number },
    trade_offs: string[]
  }>
}
```

---

#### POST `/api/v1/planning/allocate-budget`

**Purpose**: Allocate budget across channels based on funnel allocation

**Input Parameters**:
```typescript
{
  client_id: string,      // Required: Client identifier
  total_budget: number,   // Required: Total budget amount
  awareness: number,      // Required: Percentage (0-100)
  consideration: number,  // Required: Percentage (0-100)
  performance: number     // Required: Percentage (0-100)
}
```

**Output Schema**:
```typescript
{
  total_budget: number,
  funnel_allocation: {
    awareness: number,
    consideration: number,
    performance: number
  },
  channel_allocations: Array<{
    channel: string,
    budget: number,
    percentage: number,
    expected_leads: number,
    expected_cpa: number,
    funnel_stage: string,
    risk_level: string
  }>,
  summary: {
    total_expected_leads: number,
    total_expected_revenue: number,
    overall_roas: number,
    risk_score: number,
    diversification_confidence: number
  },
  recommendations: string[]
}
```

---

#### POST `/api/v1/planning/predict-scenario`

**Purpose**: Advanced scenario prediction with spline modeling and adstock

**Input Parameters**:
```typescript
{
  client_id: string,      // Required: Client identifier
  total_budget: number,   // Required: Total budget
  awareness: number,      // Required: Percentage (0-100)
  consideration: number,  // Required: Percentage (0-100)
  performance: number,    // Required: Percentage (0-100)
  target_leads: number,   // Required: Target lead count
  target_cpa: number      // Required: Target cost per acquisition
}
```

**Output Schema**:
```typescript
{
  scenario_inputs: {
    total_budget: number,
    funnel_allocation: {
      awareness: number,
      consideration: number,
      performance: number
    },
    client_targets: {
      target_leads: number,
      target_cpa: number
    }
  },
  predictions: {
    predicted_leads: number,
    incremental_leads: number,
    confidence_level: number,
    target_achievement: number  // 0-1 ratio
  },
  channel_predictions: {
    [channel_name: string]: {
      predicted_leads: number,
      confidence_interval: {
        lower: number,
        upper: number
      },
      incremental_value: number,
      saturation_level: number,  // 0-1
      adstock_remaining: number,  // 0-1
      refresh_recommendation: string  // "immediate" | "soon" | "monitor"
    }
  },
  adstock_analysis: Array<{
    channel: string,
    current_saturation: number,
    decay_rate: number,
    days_until_refresh: number,
    saturation_velocity: string,
    refresh_urgency: string
  }>,
  overmind_evaluation: {
    score: number,       // 0-1
    assessment: string
  },
  token_outcome: {
    reward: number,
    penalty: number,
    net_tokens: number
  },
  optimization_recommendations: string[]
}
```

---

#### GET `/api/v1/planning/spline-prediction`

**Purpose**: Get spline-based prediction for single channel

**Input Parameters**:
```typescript
{
  client_id: string,  // Required: Client identifier
  channel: string,    // Required: Channel name
  budget: number      // Required: Budget amount
}
```

**Output Schema**:
```typescript
{
  channel: string,
  budget: number,
  prediction: {
    predicted_leads: number,
    confidence_interval: {
      lower: number,
      upper: number
    },
    incremental_value: number,
    saturation_level: number,
    adstock_remaining: number,
    refresh_recommendation: string
  }
}
```

---

#### GET `/api/v1/planning/adstock-saturation`

**Purpose**: Get adstock saturation analysis

**Input Parameters**:
```typescript
{
  client_id: string,            // Required: Client identifier
  channel: string,              // Required: Channel name
  days_since_refresh: number    // Required: Days since last refresh
}
```

**Output Schema**:
```typescript
{
  channel: string,
  days_since_refresh: number,
  saturation_analysis: {
    current_saturation: number,  // 0-1
    decay_rate: number,         // 0-1
    days_until_refresh: number,
    saturation_velocity: string, // "increasing" | "stable" | "decreasing"
    refresh_urgency: string     // "immediate" | "soon" | "monitor"
  },
  recommendations: {
    refresh_timing: string,
    action: string
  }
}
```

---

#### POST `/api/v1/planning/realtime-prediction`

**Purpose**: Real-time prediction for slider updates (lightweight endpoint)

**Input Parameters**:
```typescript
{
  client_id: string,      // Required: Client identifier
  awareness: number,      // Required: Percentage (0-100)
  consideration: number,  // Required: Percentage (0-100)
  performance: number,    // Required: Percentage (0-100)
  total_budget: number    // Optional: Default 3500.0
}
```

**Output Schema**:
```typescript
{
  funnel_allocation: {
    awareness: number,
    consideration: number,
    performance: number
  },
  predictions: {
    total_leads: number,
    total_incremental: number,
    channel_breakdown: {
      [channel_name: string]: {
        leads: number,
        incremental: number,
        saturation: number
      }
    }
  },
  risk_score: number,
  confidence: number
}
```

---

#### GET `/api/v1/planning/channel-mappings`

**Purpose**: Get channel to funnel stage mappings

**Input Parameters**:
```typescript
{
  client_id: string  // Required: Client identifier
}
```

**Output Schema**:
```typescript
{
  channel_mappings: Array<{
    channel_name: string,
    funnel_stage: string,
    funnel_stage_id: string,
    default_allocation_weight: number,
    typical_cpa: number,
    typical_conversion_rate: number,
    is_active: boolean,
    updated_at: string  // ISO 8601 datetime
  }>,
  by_funnel_stage: {
    [stage_name: string]: Array<{
      channel_name: string,
      funnel_stage: string,
      funnel_stage_id: string,
      default_allocation_weight: number,
      typical_cpa: number,
      typical_conversion_rate: number,
      is_active: boolean,
      updated_at: string
    }>
  },
  funnel_stages: {
    [stage_name: string]: {
      description: string,
      risk_level: string,
      expected_roi_range: {
        min: number,
        max: number
      },
      time_to_conversion: string
    }
  },
  total_channels: number,
  last_updated: string | null
}
```

---

#### POST `/api/v1/planning/channel-mappings`

**Purpose**: Create or update channel mapping

**Input Parameters**:
```typescript
{
  client_id: string,              // Required: Client identifier
  channel_name: string,           // Required: Channel name
  funnel_stage: string,           // Required: Funnel stage name
  default_weight: number,         // Optional: Default 0.3
  typical_cpa: number,            // Optional: Default 25.0
  typical_conversion_rate: number // Optional: Default 0.03
}
```

**Output Schema**:
```typescript
{
  action: string,  // "created" | "updated"
  channel_mapping: {
    id: string,
    channel_name: string,
    funnel_stage: string,
    default_allocation_weight: number,
    typical_cpa: number,
    typical_conversion_rate: number
  }
}
```

---

#### GET `/api/v1/planning/funnel-stages`

**Purpose**: Get all funnel stage definitions

**Input Parameters**: None (query params only)

**Output Schema**:
```typescript
{
  funnel_stages: Array<{
    id: string,
    name: string,
    description: string,
    risk_level: string,
    expected_roi_range: {
      min: number,
      max: number
    },
    time_to_conversion: string
  }>,
  total_stages: number
}
```

---

### Media Buying Flow Endpoints

#### POST `/api/v1/media-buying/execute-allocation`

**Purpose**: Execute allocation plan via Thompson sampling

**Input Parameters**:
```typescript
{
  client_id: string,       // Required: Client identifier
  allocation_plan: string  // Required: JSON string of channel allocations
  // Example: '{"meta": 1000, "google": 900, "tiktok": 1000, "microsoft": 600}'
}
```

**allocation_plan Schema** (parsed JSON):
```typescript
{
  [channel_name: string]: number  // Budget amount per channel
}
```

**Output Schema**:
```typescript
{
  execution: {
    platform_allocations: {
      [channel_name: string]: number  // Executed budget
    },
    bids_placed: {
      [channel_name: string]: number  // Bid amount
    },
    total_spend: number,
    expected_conversions: number,
    execution_timestamp: string  // ISO 8601 datetime
  },
  method: string,  // "thompson_sampling"
  status: string   // "completed"
}
```

---

#### POST `/api/v1/media-buying/execute-complete`

**Purpose**: Execute complete media buying flow with adstock analysis

**Input Parameters**:
```typescript
{
  client_id: string,         // Required: Client identifier
  allocation_plan: string,   // Required: JSON string of channel allocations
  daily_conversions: string  // Required: JSON string of daily conversions per channel
  // Example: '{"meta": [100, 95, 90], "google": [120, 115, 110]}'
}
```

**daily_conversions Schema** (parsed JSON):
```typescript
{
  [channel_name: string]: number[]  // Array of daily conversion counts
}
```

**Output Schema**:
```typescript
{
  execution: {
    platform_allocations: {
      [channel_name: string]: number
    },
    bids_placed: {
      [channel_name: string]: number
    },
    total_spend: number,
    expected_conversions: number
  },
  adstock_signals: {
    [channel_name: string]: {
      lambda_decay: number,
      signal: string,  // "hold" | "reduce" | "exit"
      confidence: string
    }
  },
  bid_recommendations: Array<{
    channel: string,
    recommended_bid: number,
    confidence: number,
    reasoning: string
  }>,
  performance_metrics: {
    total_spend: number,
    expected_conversions: number,
    platform_count: number,
    adstock_hold_count: number,
    adstock_reduce_count: number
  },
  status: string
}
```

---

#### GET `/api/v1/media-buying/campaign-performance`

**Purpose**: Get performance data for a campaign

**Input Parameters**:
```typescript
{
  client_id: string,    // Required: Client identifier
  campaign_id: string   // Required: Campaign identifier
}
```

**Output Schema**:
```typescript
{
  campaign_id: string,
  campaign_name: string,
  performance: {
    impressions: number,
    clicks: number,
    ctr: number,              // Click-through rate (0-1)
    conversions: number,
    cost_per_conversion: number,
    conversion_rate: number,  // (0-1)
    cost: number,
    revenue: number,
    roas: number
  },
  performance_by_day: Array<{
    date: string,      // ISO 8601 date
    impressions: number,
    clicks: number,
    conversions: number
  }>
}
```

---

#### GET `/api/v1/media-buying/thompson-allocation`

**Purpose**: Get Thompson sampling allocation results

**Input Parameters**:
```typescript
{
  client_id: string,    // Required: Client identifier
  total_budget: number  // Required: Total budget amount
}
```

**Output Schema**:
```typescript
{
  total_budget: number,
  thompson_sampling_allocations: {
    [channel_name: string]: number  // Budget allocation
  },
  method: string,  // "beta_bernoulli_bandit"
  confidence: number,
  exploration_budget: number,
  exploitation_budget: number
}
```

---

#### GET `/api/v1/media-buying/adstock-signals`

**Purpose**: Get adstock decay signals for all channels

**Input Parameters**:
```typescript
{
  client_id: string,         // Required: Client identifier
  daily_conversions: string  // Required: JSON string of daily conversions
}
```

**Output Schema**:
```typescript
{
  adstock_signals: {
    [channel_name: string]: {
      lambda_decay: number,
      std_error: number,
      initial_effect: number,
      confidence: string,
      signal: string  // "hold" | "reduce" | "exit"
    }
  },
  summary: {
    total_channels: number,
    hold_signals: number,
    reduce_signals: number,
    exit_signals: number
  }
}
```

---

### Intelligence Flow Endpoints

#### GET `/api/v1/intelligence/tavily-results`

**Purpose**: Get market intelligence using Tavily scraping

**Input Parameters**:
```typescript
{
  client_id: string,    // Required: Client identifier
  topic: string,        // Required: Topic to research
  max_results: number   // Optional: Default 15
}
```

**Output Schema**:
```typescript
{
  topic: string,
  results_count: number,
  answer: string,
  query_time: number,
  results: Array<{
    title: string,
    url: string,
    content: string,
    score: number,
    published_date: string | null
  }>
}
```

---

#### POST `/api/v1/intelligence/complete-pipeline`

**Purpose**: Execute complete intelligence → analysis → activation pipeline

**Input Parameters**:
```typescript
{
  client_id: string,         // Required: Client identifier
  topic: string,             // Required: Topic to research
  campaign_type: string,     // Optional: Default "SEARCH"
  daily_budget: number,      // Optional: Default 500.0
  match_type: string,        // Optional: Default "PHRASE"
}
```

**Campaign Type Enum**: `SEARCH` | `DISPLAY` | `VIDEO`
**Match Type Enum**: `BROAD` | `PHRASE` | `EXACT`

**Output Schema**:
```typescript
{
  tavily_intelligence: {
    query: string,
    results_count: number,
    answer: string
  },
  bert_analysis: {
    keywords_generated: number,
    analyzed_keywords: Array<{
      keyword: string,
      relevance_score: number,
      intent_score: number,
      volume_estimate: number,
      competition_score: number,
      suggested_bid: number,
      category: string
    }>
  },
  google_ads_campaign: {
    campaign_id: string,
    campaign_name: string,
    campaign_type: string,
    status: string,
    daily_budget: number
  },
  ad_groups: Array<{
    ad_group_id: string,
    ad_group_name: string,
    status: string,
    bid_amount: number
  }>,
  keywords: Array<{
    keyword_text: string,
    match_type: string,
    bid_amount: number,
    status: string
  }>,
  ads: Array<{
    ad_name: string,
    ad_group_id: string,
    headlines: string[],
    descriptions: string[],
    status: string
  }>,
  summary: {
    ad_groups_created: number,
    keywords_added: number,
    ads_created: number
  }
}
```

---

#### POST `/api/v1/intelligence/tavily-to-keywords`

**Purpose**: Tavily scraping + BERT keyword generation

**Input Parameters**:
```typescript
{
  client_id: string,     // Required: Client identifier
  topic: string,         // Required: Topic to research
  max_keywords: number   // Optional: Default 50
}
```

**Output Schema**:
```typescript
{
  topic: string,
  tavily_intelligence: {
    results_count: number,
    answer: string,
    query_time: number
  },
  thrad_bert_analysis: {
    keywords_generated: number,
    analyzed_keywords: Array<{
      keyword: string,
      relevance_score: number,
      intent_score: number,
      volume_estimate: number,
      competition_score: number,
      suggested_bid: number,
      category: string
    }>
  },
  intelligence_summary: {
    key_themes: string[],
    trending_concepts: string[],
    consumer_insights: string[],
    market_opportunities: string[]
  }
}
```

---

#### POST `/api/v1/intelligence/create-google-campaign`

**Purpose**: Create Google Ads campaign from keywords

**Input Parameters**:
```typescript
{
  client_id: string,         // Required: Client identifier
  topic: string,             // Required: Campaign topic
  keywords: string[],        // Optional: Array of keywords
  campaign_type: string,     // Optional: Default "SEARCH"
  daily_budget: number,      // Optional: Default 500.0
  match_type: string,        // Optional: Default "PHRASE"
}
```

**Output Schema**:
```typescript
{
  campaign: {
    campaign_id: string,
    campaign_name: string,
    campaign_type: string,
    status: string,
    daily_budget: number,
    start_date: string,
    end_date: string
  },
  ad_groups: Array<{
    ad_group_id: string,
    ad_group_name: string,
    status: string,
    bid_amount: number,
    bid_strategy: string
  }>,
  keywords: Array<{
    keyword_text: string,
    match_type: string,
    bid_amount: number,
    status: string
  }>,
  ads: Array<{
    ad_name: string,
    ad_group_id: string,
    ad_type: string,
    headlines: string[],
    descriptions: string[],
    status: string
  }>,
  summary: {
    ad_groups_created: number,
    keywords_added: number,
    ads_created: number
  }
}
```

---

#### GET `/api/v1/intelligence/campaign-performance`

**Purpose**: Get Google Ads campaign performance

**Input Parameters**:
```typescript
{
  client_id: string,    // Required: Client identifier
  campaign_id: string   // Required: Campaign identifier
}
```

**Output Schema**:
```typescript
{
  campaign_id: string,
  campaign_name: string,
  performance: {
    impressions: number,
    clicks: number,
    ctr: number,
    conversions: number,
    cost_per_conversion: number,
    conversion_rate: number,
    cost: number,
    revenue: number,
    roas: number
  },
  ad_group_performance: Array<{
    ad_group_id: string,
    ad_group_name: string,
    impressions: number,
    clicks: number,
    conversions: number,
    cost: number
  }>
}
```

---

#### POST `/api/v1/intelligence/optimize-keywords`

**Purpose**: Optimize campaign keywords using BERT analysis

**Input Parameters**:
```typescript
{
  client_id: string,    // Required: Client identifier
  ad_group_id: string,  // Required: Google Ads ad group ID
  topic: string         // Required: Topic for new keyword generation
}
```

**Output Schema**:
```typescript
{
  ad_group_id: string,
  current_performance: {
    underperforming_keywords: string[]
  },
  new_keywords_from_bert: string[],
  optimization_recommendations: Array<{
    keyword: string,
    action: string,  // "pause" | "add" | "bid_adjust"
    reasoning: string
  }>,
  summary: {
    keywords_to_pause: number,
    keywords_to_add: number,
    total_recommendations: number
  }
}
```

---

#### GET `/api/v1/intelligence/realtime-keywords`

**Purpose**: Generate real-time keywords using enhanced Tavily

**Input Parameters**:
```typescript
{
  client_id: string,  // Required: Client identifier
  topic: string,      // Required: Topic to generate keywords for
  platform: string    // Optional: Default "google"
}
```

**Output Schema**:
```typescript
{
  topic: string,
  platform: string,
  positive_keywords: Array<{
    keyword: string,
    search_volume: number,
    competition: string,  // "low" | "medium" | "high"
    avg_cpc: number,
    competition_index: number
  }>,
  negative_keywords: string[],
  keyword_opportunities: Array<{
    keyword: string,
    opportunity_score: number,
    frequency: number
  }>,
  total_keywords: number,
  generated_at: string  // ISO 8601 datetime
}
```

---

## Agent Specifications

### PlanningService Agent

**Location**: `services/planning/service.py`

**Input Schema**:
```typescript
{
  client_context: {
    industry: string,
    business_goal: string,  // "customer_acquisition" | "brand_awareness" | "retention" | "revenue_growth"
    current_budget: number,
    target_leads: number,
    target_cpa: number,
    seasonality: string  // "peak" | "normal" | "low"
  },
  total_budget: number,
  funnel_allocation?: {
    awareness: number,
    consideration: number,
    performance: number
  },
  selected_channels?: string[],
  days_since_refresh?: {
    [channel_name: string]: number
  }
}
```

**Output Schema**:
```typescript
{
  allocation_plan: {
    funnel_allocation: {
      awareness: number,
      consideration: number,
      performance: number
    },
    channel_allocations: {
      [channel_name: string]: number
    },
    expected_leads: number,
    expected_revenue: number,
    risk_score: number,
    confidence: number,
    recommendations: string[]
  },
  prediction: {
    predicted_leads: number,
    incremental_leads: number,
    confidence_level: number,
    channel_predictions: {
      [channel_name: string]: {
        predicted_leads: number,
        confidence_interval: [number, number],
        incremental_value: number,
        saturation_level: number,
        adstock_remaining: number,
        refresh_recommendation: string
      }
    },
    overmind_score: number,
    token_reward: number,
    token_penalty: number,
    optimization_recommendations: string[]
  },
  adstock_analysis: Array<{
    channel: string,
    current_saturation: number,
    decay_rate: number,
    days_until_refresh: number,
    saturation_velocity: string,
    refresh_urgency: string
  }>,
  token_outcome: {
    reward: number,
    penalty: number,
    net_tokens: number
  }
}
```

---

### MediaBuyingService Agent

**Location**: `services/media_buying/service.py`

**Input Schema**:
```typescript
{
  allocation_plan: {
    [channel_name: string]: number  // Budget per channel
  },
  channel_performance: {
    [channel_name: string]: {
      expected_leads: number,
      actual_leads: number,
      conversions: number,
      spend: number
    }
  },
  daily_conversions?: {
    [channel_name: string]: number[]  // Daily conversion counts
  },
  platform_configs?: {
    [platform_name: string]: {
      // Platform-specific configuration
    }
  }
}
```

**Output Schema**:
```typescript
{
  execution: {
    platform_allocations: {
      [channel_name: string]: number
    },
    bids_placed: {
      [channel_name: string]: number
    },
    total_spend: number,
    expected_conversions: number,
    execution_timestamp: string
  },
  adstock_signals: {
    [channel_name: string]: {
      decay_rate: number,
      std_error: number,
      initial_effect: number,
      confidence: string,
      signal: string
    }
  },
  bid_recommendations: Array<{
    channel: string,
    recommended_bid: number,
    confidence: number,
    reasoning: string
  }>,
  performance_metrics: {
    total_spend: number,
    expected_conversions: number,
    platform_count: number,
    adstock_hold_count: number,
    adstock_reduce_count: number
  }
}
```

---

### Intelligence Pipeline Agent

**Location**: `services/intelligence/` (TavilyClient + ThradBERTClient + GoogleAdsManager)

**Input Schema**:
```typescript
{
  topic: string,
  tavily_config?: {
    max_results: number,
    search_depth: string  // "basic" | "advanced"
  },
  bert_config?: {
    max_keywords: number,
    model_path?: string
  },
  campaign_config?: {
    campaign_type: string,  // "SEARCH" | "DISPLAY" | "VIDEO"
    daily_budget: number,
    goal: string,
    platform: string,
    headlines: string[],
    descriptions: string[],
    final_url: string
  },
  keyword_config?: {
    match_type: string,  // "BROAD" | "PHRASE" | "EXACT"
    default_bid: number,
    max_keywords: number
  }
}
```

**Output Schema**:
```typescript
{
  tavily_intelligence: {
    query: string,
    results: Array<{
      title: string,
      url: string,
      content: string,
      score: number
    }>,
    answer: string,
    query_time: number
  },
  bert_keywords: Array<{
    keyword: string,
    relevance_score: number,
    intent_score: number,
    volume_estimate: number,
    competition_score: number,
    suggested_bid: number,
    category: string
  }>,
  bert_summary: {
    key_themes: string[],
    trending_concepts: string[],
    consumer_insights: string[],
    market_opportunities: string[]
  },
  google_ads_campaign: {
    campaign_id: string,
    campaign_name: string,
    campaign_type: string,
    status: string,
    daily_budget: number,
    start_date: string,
    end_date: string
  },
  ad_groups: Array<{
    ad_group_id: string,
    ad_group_name: string,
    status: string,
    bid_amount: number,
    bid_strategy: string
  }>,
  keywords: Array<{
    keyword_text: string,
    match_type: string,
    bid_amount: number,
    status: string
  }>,
  ads: Array<{
    ad_name: string,
    ad_group_id: string,
    ad_type: string,
    headlines: string[],
    descriptions: string[],
    status: string
  }>
}
```

---

### Bloomberg Terminal API Endpoints

**Purpose**: Real-time dashboard data for Bloomberg Terminal-style UI

#### GET `/terminal/header-stats`

**Purpose**: Get real-time header statistics (budget, leads, ROAS, tokens)

**Input Parameters**: None

**Output Schema**:
```typescript
{
  budget: number,      // Current budget amount
  leads: number,       // Total leads generated
  roas: number,        // Return on ad spend ratio
  tokens: number       // Token balance
}
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/channel-metrics`

**Purpose**: Get channel performance metrics with trends

**Input Parameters**: None

**Output Schema**:
```typescript
Array<{
  name: string,           // Channel name (e.g., "META", "GOOGLE")
  spend: number,          // Spend amount
  leads: number,          // Number of leads
  cpa: number,            // Cost per acquisition
  trend: "up" | "down"    // Performance trend
}>
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/campaign-signals`

**Purpose**: Get campaign signals (BUY/HOLD/STOP) with confidence scores

**Input Parameters**: None

**Output Schema**:
```typescript
Array<{
  name: string,                    // Campaign name
  signal: "BUY" | "HOLD" | "STOP",  // Analyst-style signal
  confidence: number,               // Confidence score (0-100)
  spend: number,                    // Campaign spend
  roas: number                      // ROAS
}>
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/adstock-saturation`

**Purpose**: Get adstock saturation levels and refresh signals

**Input Parameters**: None

**Output Schema**:
```typescript
Array<{
  channel: string,              // Channel name
  saturation: number,           // Saturation level (0-1)
  days_until_refresh: number,   // Days until creative refresh needed
  signal: "HOLD" | "REFRESH"    // Action signal
}>
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/strategy-brief`

**Purpose**: Get strategy brief funnel data by mode

**Input Parameters**:
```typescript
{
  mode: "leads" | "revenue" | "spend"  // Query parameter, default: "leads"
}
```

**Output Schema**:
```typescript
{
  mode: "leads" | "revenue" | "spend",
  funnel: {
    awareness: number,      // Awareness value
    consideration: number,  // Consideration value
    performance: number     // Performance value
  },
  timeline: Array<{
    month: string,   // Month abbreviation (e.g., "Jan")
    value: number    // Monthly value
  }>
}
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/strategy-docs`

**Purpose**: Get strategy documentation (previous strategy, actions, results)

**Input Parameters**: None

**Output Schema**:
```typescript
{
  previous_strategy: string,           // Previous strategy description
  agent_actions: string[],             // List of agent actions taken
  algorithm_results: {
    [algorithm_name: string]: string   // Algorithm-specific results
  },
  fine_tuning_applied: string[],       // List of fine-tuning changes
  last_updated: string                 // ISO timestamp
}
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/budget-scenarios`

**Purpose**: Get three budget allocation scenarios (conservative/moderate/growth)

**Input Parameters**: None

**Output Schema**:
```typescript
{
  conservative: {
    name: "conservative",
    roas: number,
    risk_level: "low" | "medium" | "high",
    pillar_allocation: {
      awareness: number,
      consideration: number,
      performance: number
    },
    channel_allocation: {
      [channel_name: string]: number  // Percentage allocation
    },
    expected_return: number
  },
  moderate: { /* same structure */ },
  growth: { /* same structure */ }
}
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/budget-scenarios/{scenario_name}`

**Purpose**: Get detailed information for a specific scenario

**Input Parameters**:
```typescript
{
  scenario_name: "conservative" | "moderate" | "growth"  // Path parameter
}
```

**Output Schema**: Same as single scenario object in `/terminal/budget-scenarios`

**HTTP Status Codes**:
- `200`: Success
- `404`: Scenario not found

---

#### GET `/terminal/intelligence-results`

**Purpose**: Get intelligence results from Tavily/BERT with classification

**Input Parameters**:
```typescript
{
  query: string  // Optional query string
}
```

**Output Schema**:
```typescript
Array<{
  topic: string,                           // Intelligence topic
  source: "TAVILY" | "BERT",               // Data source
  relevance: number,                       // Relevance score (0-1)
  classification: "H" | "G" | "A"          // DisBERT classification
}>
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/content-gaps`

**Purpose**: Get content gap matrix analysis

**Input Parameters**: None

**Output Schema**:
```typescript
Array<{
  topic: string,                        // Content topic
  severity: "high" | "medium" | "low",  // Gap severity
  gap_score: number                     // Gap score (0-100)
}>
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/algorithm-scores`

**Purpose**: Get real-time algorithm performance scores

**Input Parameters**: None

**Output Schema**:
```typescript
Array<{
  name: string,                                    // Algorithm name
  score: number,                                   // Performance score (0-100)
  status: "optimal" | "good" | "needs_attention"   // Status indicator
}>
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/agent-logs`

**Purpose**: Get agent action logs for CLI display

**Input Parameters**:
```typescript
{
  limit: number  // Query parameter, default: 20
}
```

**Output Schema**:
```typescript
Array<{
  timestamp: string,  // Time in HH:MM:SS format
  agent: string,      // Agent name
  action: string,     // Action description
  result?: string     // Optional result
}>
```

**HTTP Status Codes**:
- `200`: Success

---

#### GET `/terminal/full-dashboard`

**Purpose**: Get all dashboard data in a single request (optimized for initial load)

**Input Parameters**: None

**Output Schema**:
```typescript
{
  header_stats: { /* same as /terminal/header-stats */ },
  channel_metrics: { /* same as /terminal/channel-metrics */ },
  campaign_signals: { /* same as /terminal/campaign-signals */ },
  adstock_saturation: { /* same as /terminal/adstock-saturation */ },
  strategy_brief: {
    leads: { /* funnel data */ },
    revenue: { /* funnel data */ },
    spend: { /* funnel data */ },
    timeline: { /* timeline data */ }
  },
  strategy_docs: { /* same as /terminal/strategy-docs */ },
  budget_scenarios: { /* same as /terminal/budget-scenarios */ },
  intelligence_results: { /* same as /terminal/intelligence-results */ },
  content_gaps: { /* same as /terminal/content-gaps */ },
  algorithm_scores: { /* same as /terminal/algorithm-scores */ },
  agent_logs: { /* same as /terminal/agent-logs */ }
}
```

**HTTP Status Codes**:
- `200`: Success

---

## Common Data Types

### FunnelStageEnum
```typescript
type FunnelStageEnum = "awareness" | "consideration" | "performance"
```

### ChannelType
```typescript
type ChannelType = "meta" | "google" | "tiktok" | "microsoft" | "reddit" | "instagram" | "linkedin"
```

### BusinessGoal
```typescript
type BusinessGoal = "customer_acquisition" | "brand_awareness" | "retention" | "revenue_growth"
```

### AdstockSignal
```typescript
type AdstockSignal = "hold" | "reduce" | "exit"
```

### MatchType
```typescript
type MatchType = "BROAD" | "PHRASE" | "EXACT"
```

### CampaignType
```typescript
type CampaignType = "SEARCH" | "DISPLAY" | "VIDEO"
```

---

## Error Response Schema

All endpoints return error responses in the following format:

```typescript
{
  detail: string  // Error message
}
```

**Common HTTP Status Codes**:
- `200`: Success
- `400`: Bad Request (invalid input parameters)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

---

## Rate Limits

Current implementation: No rate limiting configured

Planned: TBD (see TODO list in HANDOVER.md)

---

## Authentication

Current implementation: No authentication configured

Planned: API key or OAuth (see TODO list in HANDOVER.md)

---

## Pagination

Current implementation: No pagination implemented

Planned: TBD for endpoints returning large datasets