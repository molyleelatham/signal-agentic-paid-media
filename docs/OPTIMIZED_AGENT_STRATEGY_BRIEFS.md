# SIGNAL Platform - Strategy Briefs with Overmind Evaluation

**Version**: 1.0
**Date**: 2025-11-28
**Purpose**: Optimized agent policies with Overmind evaluation framework

---

## Overview

This document contains optimized strategy briefs for all 5 SIGNAL platform agents, designed for Overmind evaluation and continuous improvement. Each brief includes the optimized policy, evaluation criteria, and Overmind integration specifications.

---

## Strategy Brief: Bid Strategy Agent

### Optimized Policy
See: `policies/bid_strategy_agent_optimized.md`

### Overmind Evaluation Framework

#### Evaluation Criteria
1. **Accuracy**: Bid recommendation vs. actual optimal bid (target: ±15%)
2. **ROAS Maintenance**: Percentage of decisions maintaining ROAS > 2.0 (target: 95%)
3. **Budget Compliance**: Percentage of recommendations within budget (target: 100%)
4. **Confidence Calibration**: Confidence score accuracy (target: >0.8)
5. **Reasoning Quality**: Specificity of market data references (target: 3+ data points)

#### Overmind Trace Configuration
```python
{
  "function_name": "bid_strategy_recommend",
  "input_data": {
    "campaign_id": "required",
    "platform": "required",
    "current_bid": "required",
    "target_cpa": "required",
    "market_conditions": "required",
    "performance_data": "required"
  },
  "output_validation": {
    "recommended_bid": "numeric_range",
    "confidence": "0.6-1.0",
    "reasoning": "min_length_50_chars",
    "risk_assessment": "enum(low,medium,high)"
  },
  "quality_thresholds": {
    "accuracy": 0.85,
    "roas_maintenance": 0.95,
    "confidence_calibration": 0.80
  }
}
```

#### Continuous Improvement Signals
- **Positive**: CPA reduction >15%, ROAS improvement >10%
- **Negative**: Budget violations, ROAS drops below 2.0
- **Retrain Signal**: Accuracy drops below 0.7 for 3 consecutive days

---

## Strategy Brief: Content Brief Agent

### Optimized Policy
See: `policies/content_brief_agent_optimized.md`

### Overmind Evaluation Framework

#### Evaluation Criteria
1. **Differentiation Score**: Average differentiation score (target: >0.75)
2. **Acceptance Rate**: Brief acceptance by creative team (target: >80%)
3. **Platform Fit**: Alignment with platform best practices (target: >85%)
4. **Confidence Calibration**: Confidence vs. actual brief quality (target: >0.75)
5. **Generation Speed**: Brief generation time (target: <30 seconds)

#### Overmind Trace Configuration
```python
{
  "function_name": "content_brief_generate",
  "input_data": {
    "gap_topic": "required",
    "gap_score": "required",
    "competitor_angles": "required",
    "target_platform": "required",
    "business_goal": "required"
  },
  "output_validation": {
    "topic": "string",
    "angle": "min_length_20_chars",
    "hook": "min_length_15_chars",
    "proof_point": "required",
    "cta": "required",
    "differentiation_score": "0.7-1.0",
    "confidence": "0.65-1.0"
  },
  "quality_thresholds": {
    "differentiation": 0.75,
    "acceptance_rate": 0.80,
    "platform_fit": 0.85
  }
}
```

#### Continuous Improvement Signals
- **Positive**: Acceptance rate >85%, differentiation score >0.8
- **Negative**: Acceptance rate <70%, differentiation score <0.65
- **Retrain Signal**: Brief rejection rate >30% for 1 week

---

## Strategy Brief: Creative Optimization Agent

### Optimized Policy
See: `policies/creative_optimization_agent_optimized.md`

### Overmind Evaluation Framework

#### Evaluation Criteria
1. **Prediction Accuracy**: Actual vs. predicted lift (target: ±10%)
2. **Performance Improvement**: Average ROAS improvement post-optimization (target: >20%)
3. **Suggestion Acceptance**: Optimization acceptance rate (target: >70%)
4. **Fatigue Detection**: Early detection of creative fatigue (target: >80%)
5. **Confidence Calibration**: Confidence vs. actual improvement (target: >0.75)

#### Overmind Trace Configuration
```python
{
  "function_name": "creative_optimization_analyze",
  "input_data": {
    "creative_id": "required",
    "creative_type": "required",
    "platform": "required",
    "performance_metrics": "required",
    "creative_assets": "required"
  },
  "output_validation": {
    "performance_score": "0-100",
    "strengths": "list_min_3",
    "weaknesses": "list_min_3",
    "optimization_suggestions": "list_min_1",
    "predicted_lift": "numeric",
    "confidence": "0.6-1.0"
  },
  "quality_thresholds": {
    "prediction_accuracy": 0.90,
    "performance_improvement": 0.20,
    "acceptance_rate": 0.70
  }
}
```

#### Continuous Improvement Signals
- **Positive**: Prediction accuracy >90%, ROAS improvement >25%
- **Negative**: Prediction accuracy <80%, negative lift predictions
- **Retrain Signal**: Prediction accuracy drops below 0.75 for 5 consecutive optimizations

---

## Strategy Brief: Market Analysis Agent

### Optimized Policy
See: `policies/market_analysis_agent_optimized.md`

### Overmind Evaluation Framework

#### Evaluation Criteria
1. **Insight Accuracy**: Validated insights vs. actual market changes (target: >85%)
2. **False Positive Rate**: Incorrect urgent flags (target: <15%)
3. **Time to Action**: Average time from insight to implementation (target: <48 hours)
4. **Source Quality**: Average number of corroborating sources (target: >2)
5. **Business Impact**: ROI of implemented insights (target: >3.0)

#### Overmind Trace Configuration
```python
{
  "function_name": "market_analysis_insight",
  "input_data": {
    "query": "required",
    "intelligence_sources": "required",
    "time_range": "required",
    "competitors": "required",
    "focus_areas": "required"
  },
  "output_validation": {
    "insight_type": "string",
    "summary": "min_length_50_chars",
    "evidence": "list_min_2",
    "confidence": "0.5-1.0",
    "actionability": "enum(immediate,short-term,long-term)",
    "urgency": "enum(critical,high,medium,low)",
    "recommendations": "list_min_1"
  },
  "quality_thresholds": {
    "insight_accuracy": 0.85,
    "false_positive_rate": 0.15,
    "source_quality": 2.0
  }
}
```

#### Continuous Improvement Signals
- **Positive**: Insight accuracy >90%, business impact >4.0
- **Negative**: False positive rate >20%, low business impact (<2.0)
- **Retrain Signal**: Insight accuracy drops below 0.75 for 2 weeks

---

## Strategy Brief: Orchestration Agent

### Optimized Policy
See: `policies/orchestration_agent_optimized.md`

### Overmind Evaluation Framework

#### Evaluation Criteria
1. **Task Completion Rate**: Percentage of tasks completed successfully (target: >95%)
2. **Execution Time**: Average orchestration time (target: <15 minutes)
3. **Agent Success Rate**: Individual agent success rate (target: >90%)
4. **Fallback Usage**: Percentage of tasks requiring fallback (target: <10%)
5. **Decision Confidence**: Average confidence on unified decisions (target: >0.8)

#### Overmind Trace Configuration
```python
{
  "function_name": "orchestration_coordinate",
  "input_data": {
    "task_type": "required",
    "context": "required",
    "priority": "required",
    "required_agents": "required",
    "constraints": "required"
  },
  "output_validation": {
    "task_id": "string",
    "status": "enum(completed,partial,failed)",
    "agent_results": "dict",
    "aggregated_decision": "dict",
    "confidence": "0.5-1.0",
    "fallback_used": "boolean",
    "execution_time": "numeric"
  },
  "quality_thresholds": {
    "completion_rate": 0.95,
    "execution_time": 900.0,  # 15 minutes
    "agent_success_rate": 0.90,
    "fallback_usage": 0.10
  }
}
```

#### Continuous Improvement Signals
- **Positive**: Completion rate >97%, execution time <10 minutes
- **Negative**: Completion rate <90%, fallback usage >15%
- **Retrain Signal**: Completion rate drops below 0.90 for 1 week

---

## Overmind Integration Setup

### Registration Script
```bash
# Register all optimized agents with Overmind
python3 scripts/register_optimized_agents.py
```

### Evaluation Pipeline
1. **Daily Evaluation**: Run Overmind evals on all agent outputs
2. **Quality Scoring**: Calculate quality scores based on criteria
3. **Threshold Monitoring**: Alert if any agent below threshold
4. **Retrain Trigger**: Automatic retrain trigger if signals met
5. **Performance Dashboard**: Track metrics over time

### Monitoring Dashboard
- Agent accuracy trends
- Confidence calibration charts
- Failure rate monitoring
- Execution time analysis
- Business impact metrics

---

## Implementation Timeline

### Phase 1: Policy Optimization (Completed)
- ✅ Optimize all 5 agent policies to new structure
- ✅ Add decision rules, constraints, edge cases, quality expectations
- ✅ Create Overmind evaluation framework

### Phase 2: Overmind Integration (Next)
- Register optimized policies with Overmind
- Set up evaluation pipeline
- Configure quality thresholds
- Implement monitoring dashboard

### Phase 3: Continuous Improvement
- Daily evaluation runs
- Automatic retrain triggers
- Performance optimization
- Policy iteration based on results

---

## Success Metrics

### Overall Platform Metrics
- **Average Agent Accuracy**: Target >85%
- **Average Confidence Calibration**: Target >0.8
- **Average Task Completion Rate**: Target >95%
- **Average Business Impact**: Target ROAS >3.0

### Individual Agent Targets
| Agent | Accuracy | Confidence | Completion | Business Impact |
|-------|----------|------------|------------|----------------|
| Bid Strategy | 90% | 0.85 | 98% | ROAS +20% |
| Content Brief | 85% | 0.80 | 95% | Acceptance 85% |
| Creative Opt | 90% | 0.80 | 95% | Lift +25% |
| Market Analysis | 85% | 0.80 | 95% | ROI 4.0 |
| Orchestration | 95% | 0.85 | 98% | Time <15min |

---

## Conclusion

All 5 SIGNAL platform agents have been optimized with the new policy structure including decision rules, constraints, edge cases, and quality expectations. Each agent has been configured with Overmind evaluation framework for continuous improvement and monitoring.

The optimized policies are ready for:
- Overmind registration and evaluation
- Continuous monitoring and improvement
- Performance tracking and optimization
- Business impact measurement