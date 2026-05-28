# Advanced Predictive Modeling Integration

## 🚀 New Features Added to Scenario Builder

### 1. LOESS-Based Lead Prediction
**Endpoint**: `POST /api/v1/demo/planning/predict-scenario`

The scenario builder now uses LOESS (Locally Estimated Scatterplot Smoothing) regression to predict leads based on budget allocation:

- **Non-linear predictions**: Accounts for diminishing returns at higher spend levels
- **Confidence intervals**: Provides upper/lower bounds for predictions
- **Incremental value analysis**: Shows additional leads from allocation changes vs baseline
- **Channel-specific modeling**: Each channel has its own historical performance curve

**Example Response**:
```json
{
  "predictions": {
    "predicted_leads": 1120,
    "incremental_leads": 85,
    "confidence_level": 0.78,
    "target_achievement": 1.12
  },
  "channel_predictions": {
    "google": {
      "predicted_leads": 145,
      "confidence_interval": {"lower": 135, "upper": 155},
      "incremental_value": 25,
      "saturation_level": 0.45,
      "adstock_remaining": 0.72
    }
  }
}
```

### 2. Adstock Saturation Analysis
**Endpoints**: 
- `GET /api/v1/demo/planning/adstock-saturation`
- Included in `POST /api/v1/demo/planning/predict-scenario`

Analyzes when creatives should be refreshed based on saturation modeling:

- **Current saturation**: 0-1 scale showing how saturated the creative is
- **Decay rate**: Lambda parameter for each channel's adstock decay
- **Days until refresh**: Recommended timing for creative refresh
- **Saturation velocity**: Whether saturation is increasing, stable, or decreasing
- **Refresh urgency**: immediate, soon, or monitor

**Example Response**:
```json
{
  "saturation_analysis": {
    "current_saturation": 0.72,
    "decay_rate": 0.7,
    "days_until_refresh": 5,
    "saturation_velocity": "increasing",
    "refresh_urgency": "soon"
  },
  "recommendations": {
    "refresh_timing": "Refresh in 5 days",
    "action": "Monitor performance"
  }
}
```

### 3. Overmind Integration
**Included in**: `POST /api/v1/demo/planning/predict-scenario`

The scenario builder now integrates with Overmind for real-time evaluation:

- **Overmind score**: 0-1 evaluation of scenario quality
- **Goal alignment**: Assesses how well the scenario aligns with client targets
- **Optimization recommendations**: AI-powered suggestions for improvement
- **Quality criteria evaluation**: Multi-dimensional assessment

**Scoring Factors**:
- Lead achievement score (50% weight)
- Funnel balance score (30% weight)
- Historical improvement score (20% weight)

### 4. Token Reward/Penalty System
**Included in**: `POST /api/v1/demo/planning/predict-scenario`

The attention token economy is integrated into scenario evaluation:

**Token Rewards**:
- Base reward: Up to 50 tokens for lead achievement
- CPA efficiency bonus: Up to 30 tokens for beating CPA target
- Overmind multiplier: 1.0-1.5x based on scenario quality

**Token Penalties**:
- Lead target penalty: 20 tokens per missed lead (below 80% target)
- CPA penalty: 15 tokens per 10% over target CPA

**Example**:
```json
{
  "token_outcome": {
    "reward": 67.5,
    "penalty": 0.0,
    "net_tokens": 67.5
  }
}
```

### 5. Real-Time Slider Predictions
**Endpoint**: `POST /api/v1/demo/planning/realtime-prediction`

Lightweight endpoint for fast UI updates as sliders move:

- **Real-time lead predictions**: Updates as sliders change
- **Channel-level breakdown**: Shows impact per channel
- **Instant risk/confidence**: Updates risk score and confidence level
- **Optimized for speed**: Designed for smooth UI interactions

## 📊 How It Works in the Demo

### Scenario Builder Flow:

1. **User adjusts sliders** (awareness/consideration/performance)
2. **Real-time prediction** shows immediate lead impact
3. **LOESS modeling** predicts leads based on historical curves
4. **Adstock analysis** shows which channels need creative refresh
5. **Overmind evaluation** scores scenario quality
6. **Token calculation** shows reward/penalty outcome
7. **Optimization recommendations** suggest improvements

### Data Model Updates:

**New Database Table**: `adstock_decay`
- Tracks creative saturation per campaign
- Lambda decay parameters for each channel
- Refresh timing recommendations

**Enhanced Demo Data**:
- Historical performance curves for LOESS modeling
- Adstock decay parameters by channel
- Days since creative refresh per campaign
- Client targets for token calculations

## 🔧 API Usage Examples

### Complete Scenario Prediction:
```bash
curl -X POST "http://localhost:8000/api/v1/demo/planning/predict-scenario?client_id={client_id}&total_budget=3500&awareness=25&consideration=35&performance=40&target_leads=1000&target_cpa=25"
```

### Real-time Slider Updates:
```bash
curl -X POST "http://localhost:8000/api/v1/demo/planning/realtime-prediction?client_id={client_id}&awareness=30&consideration=30&performance=40&total_budget=3500"
```

### Single Channel LOESS Prediction:
```bash
curl "http://localhost:8000/api/v1/demo/planning/loess-prediction?client_id={client_id}&channel=google&budget=1000"
```

### Adstock Saturation Check:
```bash
curl "http://localhost:8000/api/v1/demo/planning/adstock-saturation?client_id={client_id}&channel=tiktok&days_since_refresh=21"
```

## 🎯 Demo Script Integration

The enhanced scenario builder now supports the complete demo flow:

1. **Slider interaction**: Real-time predictions as user adjusts funnel allocation
2. **Visual feedback**: Shows incremental value of allocation changes
3. **Saturation indicators**: Warns when channels need creative refresh
4. **Overmind scoring**: Shows AI evaluation of scenario quality
5. **Token gamification**: Displays reward/penalty for scenario performance
6. **Optimization tips**: AI recommendations for improving the scenario

## 📈 Key Metrics Exposed

- **Predicted leads**: LOESS-based with confidence intervals
- **Incremental value**: Additional leads from allocation changes
- **Saturation level**: 0-1 scale showing diminishing returns
- **Adstock remaining**: Remaining creative effectiveness
- **Refresh urgency**: When to refresh creatives
- **Overmind score**: AI evaluation of scenario quality
- **Token outcome**: Expected reward/penalty
- **Confidence level**: Overall prediction confidence

This creates a sophisticated scenario builder that combines statistical modeling, AI evaluation, and gamification to help Gymshark optimize their marketing budget allocation!