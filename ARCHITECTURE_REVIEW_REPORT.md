# SIGNAL Platform Architecture Review & Restructuring Plan

## Executive Summary

This report provides a comprehensive review of the SIGNAL platform codebase, assessing connectedness, logic consistency, naming conventions, and proposing a restructuring into two distinct flows: **Planning** and **Media Buying**.

---

## 1. CONNECTEDNESS ANALYSIS

### Current State: Partially Connected

#### ✅ Working Connections
- Planning Services → API Routes (scenario_model, recommendation_engine, predictive_modeling)
- Intelligence Services → API Routes (tavily, thrad_bert)
- Platform Integration → API Routes (google_ads, mcp_connectors)
- Agents → API Main (orchestration agent)

#### ❌ Critical Disconnections

| Component | Disconnected From | Impact |
|-----------|-------------------|--------|
| **Trading Services** (thompson_allocator) | Planning Services | Budget allocation doesn't inform scenario modeling |
| **Analytics Services** (efficiency metrics) | Planning Services | P&L scores don't affect allocation decisions |
| **Intelligence → Planning** | Scenario updates | Topic clusters don't trigger scenario recalculations |
| **Bid Strategy Agent** | Allocation data | Bids made independently of budget allocation |
| **Creative Optimization** | Media Buying | Creative rotation doesn't affect bid strategy |

### Missing Integration Points

**File: `/api/routes/demo.py` (Lines 459-534)**
- Scenario builder endpoint doesn't consume Thompson sampling allocations
- CPL matrix endpoint doesn't integrate with actual trading allocations

**File: `/services/trading/thompson_allocator.py`**
- Allocates budget with no feedback to scenario modeling
- No connection to `PredictiveModelingEngine` for validation

**File: `/services/intelligence/api.py`**
- Standalone service with no planning/trading integration
- Topic clusters generated but not used in allocation

---

## 2. LOGIC CONSISTENCY ISSUES

### 🔴 Critical Issue #1: Conflicting Allocation Models

**Location**: `scenario_model.py` vs `thompson_allocator.py`

```python
# scenario_model.py: Funnel-stage allocation
- Awareness/Consideration/Performance percentages
- Channel weights within stages
- Decimal-based calculations

# thompson_allocator.py: Platform-based allocation
- Beta-Bernoulli bandit per platform
- Conversion-based updates
- Float-based allocations
```

**Problem**: Two different allocation paradigms with no reconciliation mechanism.

**Impact**: Scenario might allocate 30% to Meta (consideration) while Thompson allocates 20% to Meta (conversion-based). No way to resolve conflicts.

---

### 🔴 Critical Issue #2: Adstock Decay Inconsistency

**Location**: `predictive_modeling.py` vs `adstock_decay.py`

```python
# predictive_modeling.py (Lines 201-246):
- Uses decay_lambda for saturation
- Formula: 1 - (lambda ^ days)

# adstock_decay.py (Lines 55-122):
- Fits lambda using scipy curve_fit
- Formula: initial_effect * (lambda ^ t)
```

**Problem**: Different mathematical approaches. Predictive modeling assumes lambda is retention rate (0-1), adstock decay treats it as fitted parameter.

**Impact**: Incompatible models will give conflicting refresh recommendations.

---

### 🔴 Critical Issue #3: LOESS vs Spline Misleading

**Location**: `predictive_model.py` (Lines 98-199)

```python
def calculate_loess_prediction(self, channel, budget, historical_data=None):
    # Line 125: Uses spline interpolation, NOT LOESS
    spline = interp1d(budgets, leads, kind='cubic', fill_value='extrapolate')
```

**Problem**: Method named `calculate_loess_prediction` but uses cubic spline interpolation.

**Impact**: Misleading naming, wrong methodology claimed.

---

### 🔴 Critical Issue #4: Token Reward Mismatch

**Location**: `predictive_modeling.py` vs `analytics/asymmetric_pnl.py`

```python
# predictive_modeling.py: Calculates rewards based on:
- Lead achievement (50%), CPA efficiency (30%), Overmind score (20%)

# asymmetric_pnl.py: Different calculation entirely
```

**Problem**: Two separate token reward systems with different formulas.

**Impact**: Scenario modeling rewards don't match actual token transactions.

---

## 3. NAMING CONVENTION ISSUES

### 🔴 Critical: FunnelStage Name Conflict

**Files**: `shared/models/analytics.py` vs `services/planning/scenario_model.py`

```python
# analytics.py (Line 56)
class FunnelStage(Base):  # Database model

# scenario_model.py (Line 15)
class FunnelStage(Enum):  # Enum
```

**Impact**: Import conflicts depending on order. **Critical bug waiting to happen.**

### Other Naming Inconsistencies

| Issue | Files | Problem |
|-------|-------|---------|
| Allocation vs Budget | Multiple | Mixed terminology |
| Stage vs Funnel | Multiple | Inconsistent usage |
| Lambda vs Decay | Multiple | `decay_lambda`, `decay_rate`, `lambda_decay` |
| CPL vs CPA | Multiple | Mixed Cost Per Lead vs Cost Per Acquisition |
| Position vs Campaign | Models | Unclear relationship |
| Brief vs Content | Multiple | Inconsistent naming |

---

## 4. ARCHITECTURE RESTRUCTURING: Planning vs Media Buying

### Current State: Monolithic

```
Current (Mixed):
├── Planning Services
├── Trading Services
├── Intelligence Services
├── Platform Integration
├── Agents
└── API Routes (all mixed together)
```

**Problem**: No clear separation between strategic planning and tactical execution.

---

### Proposed Architecture: Two-Flow Separation

```
PLANNING FLOW (Strategic)
├── Intelligence Layer
│   ├── Tavily Market Scanning
│   ├── Topic Clustering (BERTopic)
│   └── Competitive Analysis
├── Analysis Layer
│   ├── Market Analysis Agent
│   ├── Topic Gap Analysis
│   └── Audience Insights
├── Planning Layer
│   ├── Scenario Modeling Engine
│   ├── Recommendation Engine
│   ├── Predictive Modeling (rename to Spline, fix LOESS)
│   └── Funnel Allocation (Awareness/Consideration/Performance)
└── Output: Budget Allocation Plan
    ├── Channel allocations
    ├── Funnel stage mix
    ├── Expected leads/ROAS
    └── Risk assessment

MEDIA BUYING FLOW (Tactical)
├── Execution Layer
│   ├── Thompson Sampling Allocator
│   ├── Bid Discovery Engine
│   └── Bid Strategy Agent
├── Placement Layer
│   ├── Creative Optimization Agent
│   ├── MCP Connectors (TikTok, Meta, Google)
│   └── Google Ads Manager
├── Monitoring Layer
│   ├── Adstock Decay Monitor (unify with predictive)
│   ├── Performance Metrics
│   └── Token Calculator
└── Output: Executed Bids & Placements
    ├── Platform-specific bids
    ├── Creative placements
    ├── Performance data
    └── Token rewards/penalties
```

---

## 5. DATA ALGORITHM REVIEW

### Algorithm #1: Scenario Modeling
**Status**: ✅ Logic sound, needs naming fixes
- Funnel allocation logic is correct
- Risk scoring is appropriate
- **Fix**: Rename FunnelStage enum to FunnelStageEnum to avoid conflict

### Algorithm #2: Thompson Sampling
**Status**: ✅ Mathematically correct, needs integration
- Beta-Bernoulli implementation is correct
- **Issue**: No feedback loop to scenario modeling
- **Fix**: Connect to Planning flow for validation

### Algorithm #3: LOESS/Spline Prediction
**Status**: ❌ Misleading, needs fix
- Currently uses spline, not LOESS
- **Fix**: Rename to `calculate_spline_prediction` or implement actual LOESS
- **Fix**: Remove hardcoded fallback conversion rates

### Algorithm #4: Adstock Decay
**Status**: ❌ Conflicting implementations
- Two different formulas in different modules
- **Fix**: Unify into single implementation
- **Fix**: Standardize lambda parameter interpretation

### Algorithm #5: Recommendation Engine
**Status**: ✅ Logic sound
- Goal-based recommendations are appropriate
- **Fix**: Connect to actual performance data

### Algorithm #6: Token Calculator
**Status**: ❌ Duplicate implementations
- Two different calculation methods
- **Fix**: Unify into single source of truth

---

## 6. RECOMMENDED RESTRUCTURING PLAN

### Phase 1: Critical Fixes (Immediate)

1. **Rename FunnelStage enum** → `FunnelStageEnum` in `scenario_model.py`
2. **Unify Adstock Decay** into single module
3. **Rename LOESS prediction** → `spline_prediction` or implement actual LOESS
4. **Unify Token Calculation** into single implementation

### Phase 2: Service Separation (High Priority)

1. **Create Planning Service Boundary**
   ```python
   # services/planning/service.py
   class PlanningService:
       def __init__(self):
           self.intelligence = IntelligenceLayer()
           self.analysis = AnalysisLayer()
           self.planning = PlanningLayer()
       
       async def generate_allocation_plan(self, client_context):
           # Unified planning interface
   ```

2. **Create Media Buying Service Boundary**
   ```python
   # services/media_buying/service.py
   class MediaBuyingService:
       def __init__(self):
           self.execution = ExecutionLayer()
           self.placement = PlacementLayer()
           self.monitoring = MonitoringLayer()
       
       async def execute_allocation(self, allocation_plan):
           # Unified media buying interface
   ```

### Phase 3: API Route Separation

1. **Separate API Routes**
   ```
   api/routes/planning.py  - Planning endpoints
   api/routes/media_buying.py - Media buying endpoints
   api/routes/intelligence.py - Intelligence endpoints
   ```

2. **Create Clear User Flows**
   - Planning Flow: User adjusts sliders → sees predictions → saves allocation plan
   - Media Buying Flow: System executes plan → monitors performance → adjusts bids

### Phase 4: Integration Points

1. **Connect Planning → Media Buying**
   ```python
   # Planning output becomes Media Buying input
   allocation_plan = planning_service.generate_allocation_plan(client)
   executed_bids = media_buying_service.execute_allocation(allocation_plan)
   ```

2. **Connect Media Buying → Planning** (Feedback Loop)
   ```python
   # Media Buying performance informs next Planning cycle
   performance = media_buying_service.get_performance()
   updated_plan = planning_service.update_plan(performance)
   ```

---

## 7. SPECIFIC FILE CHANGES

### Files to Rename/Restructure

1. **Delete**: `services/intelligence/classification_integrator.py` (duplicate)
2. **Rename**: `FunnelStage` enum → `FunnelStageEnum` in `scenario_model.py`
3. **Merge**: Adstock decay implementations
4. **Restructure**: `api/routes/demo.py` → separate planning/media_buying routes
5. **Create**: `services/planning/service.py` (unified planning interface)
6. **Create**: `services/media_buying/service.py` (unified media buying interface)

### Variable Naming Standardization

| Current | Standardized | Files to Update |
|---------|--------------|-----------------|
| decay_lambda | decay_rate | All files |
| cpl | cpa (use CPA consistently) | All files |
| FunnelStage (enum) | FunnelStageEnum | scenario_model.py |
| calculate_loess_prediction | calculate_spline_prediction | predictive_modeling.py |
| platform_allocation | channel_allocation | All files |

---

## 8. USER EXPERIENCE FLOW

### Current UX: Confused

Users see all endpoints mixed together in demo.py, unclear which are planning vs execution.

### Proposed UX: Two Clear Flows

**Planning Flow**:
1. User enters budget and goals
2. Adjusts funnel allocation sliders
3. Sees LOESS-based predictions
4. Reviews Overmind evaluation
5. Saves allocation plan

**Media Buying Flow**:
1. System loads saved allocation plan
2. Executes via Thompson sampling
3. Places bids via Google Ads API
4. Monitors performance
5. Adjusts bids based on adstock
6. Calculates token rewards

---

## 9. PRIORITY MATRIX

| Issue | Priority | Complexity | Impact |
|-------|----------|------------|--------|
| FunnelStage naming conflict | 🔴 Critical | Low | High (breaks code) |
| Adstock decay unification | 🔴 Critical | Medium | High (conflicting logic) |
| LOESS/Spline naming | 🔴 Critical | Low | Medium (misleading) |
| Service separation | 🟡 High | High | High (UX improvement) |
| API route separation | 🟡 High | Medium | High (UX improvement) |
| Token calculation unification | 🟡 High | Medium | High (inconsistent rewards) |
| Thompson integration | 🟢 Medium | Medium | Medium (missing connection) |
| Variable naming standardization | 🟢 Medium | Low | Low (code quality) |

---

## 10. CONCLUSION

The SIGNAL platform has solid individual components but lacks:
1. Clear separation between Planning and Media Buying
2. Consistent naming conventions
3. Integration between services
4. Unified data algorithms

**Recommendation**: Implement Phase 1 (Critical Fixes) immediately, then Phase 2-4 for full restructuring into two distinct flows.

**Estimated Effort**:
- Phase 1: 1-2 days
- Phase 2: 3-4 days
- Phase 3: 2-3 days
- Phase 4: 2-3 days
- **Total**: 8-12 days for complete restructuring