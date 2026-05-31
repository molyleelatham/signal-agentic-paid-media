# SIGNAL Platform - Complete Architecture & Flow Integration

## ✅ All Fixes Completed

### Phase 1: Critical Fixes ✅
1. **FunnelStage Naming Conflict** - Renamed enum to FunnelStageEnum
2. **Duplicate Classification File** - Removed classification_integrator.py
3. **LOESS/Spline Naming** - Renamed to SplinePrediction

### Phase 2: Architecture Improvements ✅
4. **Unified Adstock Decay** - Created services/common/adstock_decay.py
5. **Unified PlanningService** - Created services/planning/service.py
6. **Unified MediaBuyingService** - Created services/media_buying/service.py

### Phase 3: API Route Separation ✅
7. **Planning Routes** - Created api/routes/planning.py
8. **Media Buying Routes** - Created api/routes/media_buying.py
9. **Intelligence Routes** - Created api/routes/intelligence.py
10. **Router Registration** - Updated api/main.py

### Phase 4: Variable Naming Standardization ✅
11. **decay_rate** - Standardized from decay_lambda/lambda_decay
12. **CPA** - Standardized from CPL (Cost Per Lead → Cost Per Acquisition)

---

## 📊 Complete Architecture Structure

```
services/
├── common/ (SHARED - Single Source of Truth)
│   ├── __init__.py
│   └── adstock_decay.py (unified decay engine)
│
├── planning/ (PLANNING FLOW - Strategic)
│   ├── __init__.py
│   ├── service.py (PlanningService - unified entry point)
│   ├── scenario_model.py (FunnelStageEnum, funnel allocation)
│   ├── recommendation_engine.py (AI recommendations)
│   └── predictive_modeling.py (Spline predictions, uses common adstock)
│
├── media_buying/ (MEDIA BUYING FLOW - Tactical)
│   ├── __init__.py
│   └── service.py (MediaBuyingService - unified entry point)
│       (uses Thompson allocator from trading/)
│       (uses common adstock)
│
├── trading/ (Used by Media Buying)
│   ├── thompson_allocator.py
│   ├── bid_discovery.py
│   ├── thrad_contextual_bid.py
│   └── adstock_decay.py (deprecated - replaced by common/)
│
├── intelligence/ (INTELLIGENCE LAYER)
│   ├── tavily_client.py
│   ├── thrad_bert_client.py
│   ├── disbert_thrad_classification.py
│   ├── enhanced_tavily.py
│   └── api.py
│
└── platform_integration/ (PLATFORM INTEGRATION)
    ├── google_ads_manager.py
    ├── google_ads.py
    └── mcp_connectors.py

api/
├── main.py (updated with new routers)
└── routes/
    ├── planning.py (NEW - Planning endpoints)
    ├── media_buying.py (NEW - Media Buying endpoints)
    ├── intelligence.py (NEW - Intelligence endpoints)
    └── demo.py (legacy - still functional)
```

---

## 🔄 Complete Flow Integration

### PLANNING FLOW (Strategic)

**Entry Point**: `PlanningService` in `services/planning/service.py`

```
User Input
    ↓
PlanningService.generate_allocation_plan()
    ├─ RecommendationEngine.generate_recommendation()
    │   └─ AI-powered funnel allocation suggestions
    ├─ ScenarioModelingEngine.model_scenario()
    │   └─ Portfolio-style channel allocation
    └─ PredictiveModelingEngine.calculate_scenario_prediction()
        ├─ Spline-based lead predictions
        ├─ AdstockSaturation analysis (uses common adstock)
        └─ Overmind evaluation
    ↓
PlanningOutput
    ├─ AllocationPlan (channel allocations)
    ├─ Prediction (leads, revenue, confidence)
    ├─ AdstockAnalysis (refresh timing)
    └─ TokenOutcome (rewards/penalties)
    ↓
Output to Media Buying Flow
```

**API Endpoints** (`api/routes/planning.py`):
- `GET /api/v1/planning/funnel-allocation` - Get current allocation
- `POST /api/v1/planning/funnel-allocation` - Update allocation
- `GET /api/v1/planning/recommendations` - Get AI recommendations
- `POST /api/v1/planning/allocate-budget` - Allocate budget by funnel
- `POST /api/v1/planning/predict-scenario` - Advanced scenario prediction
- `GET /api/v1/planning/spline-prediction` - Spline prediction per channel
- `GET /api/v1/planning/adstock-saturation` - Adstock saturation analysis
- `POST /api/v1/planning/realtime-prediction` - Real-time slider updates
- `GET /api/v1/planning/channel-mappings` - Get channel mappings
- `POST /api/v1/planning/channel-mappings` - Create channel mapping
- `GET /api/v1/planning/funnel-stages` - Get funnel stage definitions

---

### MEDIA BUYING FLOW (Tactical)

**Entry Point**: `MediaBuyingService` in `services/media_buying/service.py`

```
Input from Planning Flow (AllocationPlan)
    ↓
MediaBuyingService.execute_allocation_plan()
    ├─ ThompsonAllocator.allocate()
    │   └─ Beta-Bernoulli bandit algorithm
    └─ Budget distribution across platforms
    ↓
MediaBuyingService.execute_complete_media_buying()
    ├─ BidDiscoveryEngine
    ├─ AdstockDecayEngine.fit_decay_rate() (common adstock)
    │   └─ Hold/reduce/exit signals
    └─ Platform Integration
        ├─ Google Ads Manager
        └─ MCP Connectors (TikTok, Meta)
    ↓
MediaBuyingOutput
    ├─ ExecutionResult (bids placed)
    ├─ AdstockSignals (decay rates)
    ├─ BidRecommendations
    └─ PerformanceMetrics
    ↓
Output: Executed Bids + Performance Data
```

**API Endpoints** (`api/routes/media_buying.py`):
- `POST /api/v1/media-buying/execute-allocation` - Execute allocation plan
- `POST /api/v1/media-buying/execute-complete` - Complete media buying flow
- `GET /api/v1/media-buying/campaign-performance` - Get campaign performance
- `GET /api/v1/media-buying/thompson-allocation` - Get Thompson sampling results
- `GET /api/v1/media-buying/adstock-signals` - Get adstock decay signals

---

### INTELLIGENCE FLOW (Data Gathering)

**Entry Point**: Tavily Client + Thrad BERT Client

```
Topic/Query
    ↓
TavilyClient.search_and_answer()
    └─ Market intelligence scraping
    ↓
ThradBERTClient.generate_keywords_from_intelligence()
    ├─ Keyword generation (BERT analysis)
    ├─ Relevance scoring
    ├─ Intent classification
    └─ Volume estimation
    ↓
GoogleAdsManager.create_campaign_from_intelligence()
    ├─ Campaign creation
    ├─ Ad group setup
    ├─ Keyword placement
    └─ Search ad generation
    ↓
Output: Live Google Ads Campaign
```

**API Endpoints** (`api/routes/intelligence.py`):
- `GET /api/v1/intelligence/tavily-results` - Get Tavily intelligence
- `POST /api/v1/intelligence/complete-pipeline` - Execute full pipeline
- `POST /api/v1/intelligence/tavily-to-keywords` - Tavily → Keywords
- `POST /api/v1/intelligence/create-google-campaign` - Create Google campaign
- `GET /api/v1/intelligence/campaign-performance` - Get campaign performance
- `POST /api/v1/intelligence/optimize-keywords` - Optimize with BERT
- `GET /api/v1/intelligence/realtime-keywords` - Real-time keyword generation

---

## 🔗 Flow Integration Points

### Planning → Media Buying Connection

**Data Flow**:
```python
# Planning Output
planning_output = await planning_service.generate_complete_planning_output(
    client_context=context,
    total_budget=Decimal("3500.00")
)

# Extract channel allocations
allocation_plan = planning_output.allocation_plan.channel_allocations
# {"meta": 1000.0, "google": 900.0, "tiktok": 1000.0, "microsoft": 600.0}

# Media Buying Input
media_buying_output = await media_buying_service.execute_complete_media_buying(
    allocation_plan=allocation_plan,
    channel_performance=performance_data,
    daily_conversions=conversions_data
)
```

**API Integration**:
```bash
# 1. Get planning output
POST /api/v1/planning/predict-scenario
{
  "total_budget": 3500,
  "awareness": 25,
  "consideration": 35,
  "performance": 40
}
# Returns: allocation_plan with channel_allocations

# 2. Execute with Media Buying
POST /api/v1/media-buying/execute-complete
{
  "allocation_plan": "{\"meta\": 1000, \"google\": 900, ...}",
  "daily_conversions": "{\"meta\": [100, 95, 90, ...], ...}"
}
# Returns: executed bids, adstock signals, performance
```

### Media Buying → Planning Feedback Loop

**Data Flow**:
```python
# Media Buying Performance
performance_metrics = media_buying_output.performance_metrics

# Update Planning Context for Next Cycle
updated_context = ClientContext(
    industry=client.industry,
    business_goal=BusinessGoal.customer_acquisition,
    current_budget=Decimal("3500.00"),
    target_leads=int(performance_metrics["expected_conversions"] * 1.1),  # 10% growth
    target_cpa=Decimal(str(performance_metrics["current_cpa"] * 0.95)),  # 5% improvement
    seasonality="peak"
)

# Generate Updated Plan
updated_plan = await planning_service.generate_complete_planning_output(
    client_context=updated_context,
    total_budget=Decimal("3500.00")
)
```

---

## 📈 Unified Components

### Adstock Decay (services/common/adstock_decay.py)
- **Single Source of Truth**: Used by both Planning and Media Buying
- **Method**: `fit_decay_rate()` - scipy curve_fit for lambda estimation
- **Method**: `analyze_saturation()` - refresh timing recommendations
- **Standardized Naming**: `decay_rate` (not lambda_decay)

### Planning Service (services/planning/service.py)
- **Unified Entry Point**: `PlanningService`
- **Methods**:
  - `generate_allocation_plan()` - Strategic allocation
  - `generate_complete_planning_output()` - Full output with predictions
  - `get_recommendation()` - AI-powered suggestions

### Media Buying Service (services/media_buying/service.py)
- **Unified Entry Point**: `MediaBuyingService`
- **Methods**:
  - `execute_allocation_plan()` - Tactical execution
  - `execute_complete_media_buying()` - Full execution with adstock
  - `get_thompson_allocation()` - Thompson sampling results

---

## 🎯 User Experience Flow

### Planning Flow (User Interface)
1. User enters budget and goals
2. Adjusts funnel allocation sliders (awareness/consideration/performance)
3. Sees real-time spline predictions
4. Reviews Overmind evaluation score
5. Checks adstock refresh recommendations
6. Views token reward/penalty estimates
7. **Saves allocation plan**

### Media Buying Flow (Automated)
1. System loads saved allocation plan
2. Executes via Thompson sampling
3. Places bids via Google Ads API
4. Monitors performance with adstock analysis
5. Adjusts bids based on saturation
6. Calculates actual token rewards
7. **Feeds performance back to Planning** for next cycle

---

## 📝 Variable Naming Standards

| Old Name | New Name | Location |
|----------|----------|----------|
| `FunnelStage` (enum) | `FunnelStageEnum` | scenario_model.py |
| `decay_lambda` | `decay_rate` | common/adstock_decay.py, predictive_modeling.py |
| `lambda_decay` | `decay_rate` | common/adstock_decay.py |
| `cpl` | `cpa` | predictive_modeling.py, service.py |
| `LOESSPrediction` | `SplinePrediction` | predictive_modeling.py |
| `calculate_loess_prediction()` | `calculate_spline_prediction()` | predictive_modeling.py |

---

## 🚀 Complete Workflow Example

```python
# STEP 1: PLANNING FLOW
from services.planning import PlanningService, ClientContext, BusinessGoal

planning_service = PlanningService()
context = ClientContext(
    industry="fitness",
    business_goal=BusinessGoal.customer_acquisition,
    current_budget=Decimal("3500.00"),
    target_leads=1000,
    target_cpa=Decimal("25.0"),
    seasonality="peak"
)

# Generate allocation plan
planning_output = await planning_service.generate_complete_planning_output(
    client_context=context,
    total_budget=Decimal("3500.00")
)

# Output: AllocationPlan with channel_allocations
# {"meta": 1000.0, "google": 900.0, "tiktok": 1000.0, "microsoft": 600.0}

# STEP 2: MEDIA BUYING FLOW
from services.media_buying import MediaBuyingService

media_buying_service = MediaBuyingService()

# Execute allocation plan
media_buying_output = await media_buying_service.execute_complete_media_buying(
    allocation_plan=planning_output.allocation_plan.channel_allocations,
    channel_performance={"meta": {...}, "google": {...}},
    daily_conversions={"meta": [100, 95, 90], "google": [120, 115, 110]}
)

# Output: Executed bids, adstock signals, performance metrics

# STEP 3: FEEDBACK LOOP
# Use performance to update next planning cycle
updated_context = ClientContext(
    industry="fitness",
    business_goal=BusinessGoal.customer_acquisition,
    current_budget=Decimal("3500.00"),
    target_leads=int(media_buying_output.execution.expected_conversions * 1.1),
    target_cpa=Decimal(str(media_buying_output.performance_metrics["current_cpa"] * 0.95)),
    seasonality="peak"
)

# Generate updated plan
updated_plan = await planning_service.generate_complete_planning_output(
    client_context=updated_context,
    total_budget=Decimal("3500.00")
)
```

---

## ✅ Summary

**All critical architecture issues have been resolved:**
- ✅ Naming conflicts eliminated
- ✅ Duplicate code removed
- ✅ Misleading naming fixed
- ✅ Adstock decay unified
- ✅ Unified PlanningService created
- ✅ Unified MediaBuyingService created
- ✅ API routes separated
- ✅ Variable naming standardized
- ✅ Flow integration documented

**The platform now has:**
- Clear two-flow separation (Planning vs Media Buying)
- Single source of truth for shared components
- Consistent naming conventions
- Unified service interfaces
- Clear integration points between flows
- Documented workflows and data flow

**Ready for production deployment with proper Planning → Media Buying → Planning feedback loop!**