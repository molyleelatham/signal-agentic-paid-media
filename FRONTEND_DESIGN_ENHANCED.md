# SIGNAL Platform - Enhanced Frontend Design

**Version**: 3.0 (Enhanced)
**Date**: 2025-11-28
**Features**: Advanced Metrics, Strategy Documentation, Overmind Optimization Tracking

---

## Overview

This enhanced frontend specification adds:
- Comprehensive metrics and KPI tracking
- Strategy documentation with hover/click-through details
- Strategy implementation tracking with Overmind optimization changes
- Enhanced chat functionality with context awareness
- Advanced data visualization and drill-down capabilities

---

## Page 1: Enhanced Bloomberg Terminal Dashboard

### Additional Metrics Panel
```
┌─────────────────────────────────────────────────────────────────┐
│  SIGNAL TERMINAL                    GYMSHARK │  [Refresh: 5s] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Header Stats (Enhanced)                                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ ROAS: 3.25 (+55%)  CPL: £28 (-20%)  Leads: 1,120 (+40%)    │ │
│  │ Revenue: £42K/wk (+55%)  Budget: £18K  Spent: £12.5K       │ │
│  │ Win Rate: 78% (+12%)  Auction Share: 23% (+8%)             │ │
│  │ Conversion Rate: 3.5% (+0.8%)  Click-Through: 2.8% (+0.5%) │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Strategy Overview (Hover for Details)                          │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 📋 Current Strategy: "Summer Performance Push"              │ │
│  │ Status: ✅ Active  Days Running: 14  ROI: +28%               │ │
│  │                                                              │ │
│  │ [📄 View Strategy Doc]  [📊 Performance Since Strategy]    │ │
│  │ [🔄 Overmind Optimizations: 3 changes applied]               │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Enhanced Agent Signals                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ ⚡ BUY          │  │ ⏸️ HOLD         │  │ 🛑 STOP         │ │
│  │ Summer Training │  │ Performance Gear│  │ Old Campaign    │ │
│  │ £2,500 (85%)    │  │ £1,800 (72%)    │  │ £0 (0%)         │ │
│  │ ROAS: 4.2       │  │ ROAS: 3.1       │  │ ROAS: 1.8       │ │
│  │ Channel: Meta   │  │ Channel: Google  │  │ Channel: TikTok  │
│  │ 30-Day Lift: +15%│  │ 30-Day Lift: +8% │  │ 30-Day Lift: -5%│ │
│  │ [View Details]  │  │ [View Details]  │  │ [View Details]  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Strategy Documentation (Hover/Click-Through)

When hovering over "Current Strategy" or clicking "View Strategy Doc":

```
┌─────────────────────────────────────────────────────────────────┐
│  STRATEGY DOCUMENTATION: "Summer Performance Push"              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  📄 Strategy Document                                          │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Created: 2025-11-14  Author: Orchestration Agent           │ │
│  │ Version: 2.1  Last Modified: 2025-11-20 (Overmind Opt)      │ │
│  │                                                              │ │
│  │ Objective:                                                 │ │
│  │ Maximize performance of Summer Training Collection across     │ │
│  │ all platforms through aggressive bidding and creative        │ │
│  │ optimization, targeting 18-34 fitness enthusiasts.           │ │
│  │                                                              │ │
│  │ Target Metrics:                                             │ │
│  │ • ROAS: > 4.0                                               │ │
│  │ • CPA: < £25                                                │ │
│  │ • Conversion Rate: > 3.5%                                   │ │
│  │ • Auction Win Rate: > 75%                                   │ │
│  │                                                              │ │
│  │ Implementation:                                             │ │
│  │ • Increase bids on high-performing creatives by 15-25%       │ │
│  │ • Shift 20% budget from awareness to performance           │ │
│  │ • A/B test video vs static creatives                         │ │
│  │ • Expand to UK and Germany markets                          │ │
│  │                                                              │ │
│  │ [Download Full PDF]  [View in Editor]                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  📊 Performance Since Strategy                                  │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Days Since Implementation: 14                                 │ │
│  │                                                              │ │
│  │ Metric          Before    After     Change    Target         │ │
│  │ ROAS            3.25      4.20      +29%      > 4.0 ✅      │ │
│  │ CPA             £32       £28       -13%      < £25 ⚠️     │ │
│  │ Conversion Rate 2.7%      3.5%      +30%      > 3.5% ✅      │ │
│  │ Win Rate        70%       78%       +11%      > 75% ✅      │ │
│  │ Revenue/Week    £26K      £42K      +62%      +50% ✅      │ │
│  │                                                              │ │
│  │ [View Detailed Charts]  [Compare with Previous Strategy]      │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  🤖 Overmind Optimizations                                      │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ 3 optimizations applied by Overmind since strategy start:    │ │
│  │                                                              │ │
│  │ 1. Bid Adjustment Optimization                               │ │
│  │    Date: 2025-11-18                                          │ │
│  │    Change: Increased bid on gymshark leggings from £2.20→£2.75│ │
│  │    Reason: DisBERT detected +15% increase in purchase intent   │ │
│  │    Impact: ROAS +12%, Win Rate +8%                           │ │
│  │    Confidence: 0.92                                           │ │
│  │                                                              │ │
│  │ 2. Creative Rotation Optimization                             │ │
│  │    Date: 2025-11-19                                          │ │
│  │    Change: Rotated out creative A, introduced variant B        │ │
│  │    Reason: Adstock decay detected (λ=0.72)                   │ │
│  │    Impact: CTR +18%, Conversion +22%                          │ │
│  │    Confidence: 0.88                                           │ │
│  │                                                              │ │
│  │ 3. Geographic Expansion Optimization                           │ │
│  │    Date: 2025-11-21                                          │ │
│  │    Change: Expanded targeting to Germany and France           │ │
│  │    Reason: Market Analysis detected untapped demand          │ │
│  │    Impact: Leads +35%, CPA -8%                               │ │
│  │    Confidence: 0.85                                           │ │
│  │                                                              │ │
│  │ [View All Optimizations]  [Approve/Reject Changes]           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Close]                                                         │
└─────────────────────────────────────────────────────────────────┘
```

---

## Page 2: Enhanced Media Planning Dashboard

### Additional Metrics
```
┌─────────────────────────────────────────────────────────────────┐
│  MEDIA PLANNING                                    [Auto-refresh] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Keyword Intelligence Metrics                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Total Keywords Tracked: 1,500                                │ │
│  │ Active Keywords: 847  Paused: 321  Stopped: 332           │ │
│  │                                                              │ │
│  │ Performance Summary (30 Days):                               │ │
│  │ Average ROAS: 3.8  Average CPA: £21  Avg CTR: 2.6%          │ │
│  │ Total Spend: £45K  Total Revenue: £171K  Total ROI: 280%     │ │
│  │                                                              │ │
│  │ Top Performing Categories:                                   │ │
│  │ H (Purchasable): ROAS 4.2  CPA £18  Keywords: 125          │ │
│  │ E (Guidance): ROAS 3.5  CPA £23  Keywords: 340              │ │
│  │ L (Other): ROAS 2.8  CPA £26  Keywords: 382                │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  DisBERT Model Performance                                       │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Model: thrad_disbert  Version: 2.1                           │ │
│  │ Accuracy: 88%  Predictions: 1,200  Calibrated: ✅            │ │
│  │                                                              │ │
│  │ Classification Performance (30 Days):                         │ │
│  │ Category H Accuracy: 92%  False Positives: 8%                 │ │
│  │ Category E Accuracy: 85%  False Positives: 12%                │ │
│  │ Category L Accuracy: 87%  False Positives: 10%                │ │
│  │                                                              │ │
│  │ Commercial Intent Accuracy: 91%                               │ │
│  │ Transactional vs Informational: 89% accuracy                  │ │
│  │                                                              │ │
│  │ [View Model Details]  [Retrain Model]  [View Training Data]   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Keyword Hover Details
```
Hover over keyword to see:

┌─────────────────────────────────────────────────────────────────┐
│  KEYWORD: gymshark leggings                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Performance (30 Days)                                          │
│  Impressions: 125,000  Clicks: 3,750  Conversions: 150            │
│  CTR: 3.0%  CPA: £18  ROAS: 4.2  Revenue: £630                  │
│                                                                  │
│  DisBERT Classification                                          │
│  Category: H (Purchasable Products)                              │
│  Commercial Intent: 0.95 (High)                                  │
│  Confidence: 0.92                                               │
│  Should Use as Keywords: ✅ Yes (Priority 8)                     │
│                                                                  │
│  Bid History (Last 7 Days)                                      │
│  Day   Bid     Impressions  Clicks  Conv   CPA   ROAS           │
│  -7    £2.20   18,000      540     22    £20   3.5           │
│  -6    £2.25   19,500      585     24    £19   3.6           │
│  -5    £2.50   22,000      660     27    £19   3.8           │
│  -4    £2.75   25,000      750     30    £18   4.0           │
│  -3    £2.75   28,000      840     35    £17   4.1           │
│  -2    £2.75   30,000      900     38    £17   4.2           │
│  -1    £2.75   32,500      975     41    £17   4.2           │
│                                                                  │
│  Overmind Optimizations                                          │
│  • 2025-11-20: Bid increased £2.50→£2.75 (DisBERT intent +15%)│ │
│    Impact: ROAS +5%, Win Rate +8%                                │
│  • 2025-11-22: Match type changed phrase→exact (High intent)    │ │
│    Impact: CPA -12%, Conversion +18%                              │
│                                                                  │
│  Thrad Data                                                      │
│  User: user_123  Chat: chat_456  Model: thrad_disbert             │
│  Summary: User interested in gymshark leggings for summer         │
│  [View Full Thrad Data]                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Page 3: Enhanced Agent Management

### Additional Metrics
```
┌─────────────────────────────────────────────────────────────────┐
│  AGENT MANAGEMENT                                  [Last 30 Days ▼]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Agent Performance Summary                                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Agent               Executions  Success  Latency  Tokens   Cost│ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Bid Strategy        750         92%      450ms    75K     £75│ │
│  │ Content Brief       720         95%      620ms    82K     £82│ │
│  │ Creative Opt        680         89%      380ms    68K     £68│ │
│  │ Market Analysis     810         94%      520ms    95K     £95│ │
│  │ Orchestration       890         97%      890ms   110K    £110│ │
│  │                                                              │ │
│  │ Total:              3,850       93%      572ms   430K    £430│ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Overmind Optimization Tracking                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Bid Strategy Agent                                           │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Policy Version: 2.1  Last Optimized: 2025-11-25            │ │
│  │ Accuracy Improvement: 85% → 92% (+7%)                       │ │
│  │                                                              │ │
│  │ Recent Optimizations:                                       │ │
│  │ • 2025-11-23: Updated decision rules for market volatility  │ │
│  │   Impact: Accuracy +5%, Budget violations -100%             │ │
│  │ • 2025-11-24: Added edge case handling for missing data    │ │
│  │   Impact: Success rate +3%, Fallback usage -15%             │ │
│  │ • 2025-11-25: Calibrated confidence scoring                  │ │
│  │   Impact: Confidence accuracy +8%                             │ │
│  │                                                              │ │
│  │ [View All Optimizations]  [View Policy Diff]                  │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Hover Details
```
Hover over agent card to see:

┌─────────────────────────────────────────────────────────────────┐
│  AGENT: Bid Strategy Agent                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Policy Overview                                                 │
│  Version: 2.1  Last Updated: 2025-11-25                          │
│  Decision Rules: 5  Constraints: 4  Edge Cases: 4                 │
│  Quality Expectations: 3                                         │
│                                                                  │
│  Recent Performance (7 Days)                                    │
│  Day  Executions  Success  Latency  Accuracy  Cost             │ │
│  -7   108         95%      420ms    90%       £10.8            │
│  -6   112         93%      445ms    88%       £11.2            │
│  -5   105         92%      430ms    89%       £10.5            │
│  -4   110         94%      435ms    91%       £11.0            │
│  -3   115         95%      425ms    92%       £11.5            │
│  -2   108         93%      440ms    90%       £10.8            │
│  -1   110         94%      435ms    91%       £11.0            │
│                                                                  │
│  Overmind Optimizations (Last 30 Days)                           │
│  Total: 3  Approved: 3  Pending: 0  Rejected: 0                  │
│                                                                  │
│  1. Decision Rule Update (2025-11-23)                            │
│     Added: "If market competition is high and conversion > 3.5%"  │
│     Reason: Improve bid accuracy in competitive markets            │
│     Impact: Accuracy +5%, CPA -8%                                 │
│     Status: ✅ Approved  Confidence: 0.92                         │
│                                                                  │
│  2. Edge Case Handling (2025-11-24)                              │
│     Added: "Missing performance data → fallback to algorithmic"   │
│     Reason: Reduce failures when data unavailable                 │
│     Impact: Success rate +3%, Fallback -15%                        │
│     Status: ✅ Approved  Confidence: 0.88                         │
│                                                                  │
│  3. Confidence Calibration (2025-11-25)                          │
│     Added: "Confidence scores should correlate with accuracy"       │
│     Reason: Improve confidence calibration                        │
│     Impact: Confidence accuracy +8%                                │
│     Status: ✅ Approved  Confidence: 0.85                         │
│                                                                  │
│  [View Full Policy]  [View Optimization History]  [Suggest Change]│ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Page 4: Enhanced Chat Interface

### Additional Features
```
┌─────────────────────────────────────────────────────────────────┐
│  AI CHAT                                         [GPT-4 ▼]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Context Panel (New)                                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 💡 Context Awareness                                         │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Current Campaign: Summer Training Collection Launch          │ │
│  │ Current Strategy: Summer Performance Push                    │ │
│  │ Recent Optimization: Bid increased £2.20→£2.75 (2 days ago) │ │
│  │ Top Keyword: gymshark leggings (ROAS 4.2)                   │ │
│  │                                                              │ │
│  │ [Clear Context]  [Add Context Note]                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Agent Selection with Performance                                 │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Select Agent:                                              │ │
│  │  [🤖 General] [💰 Bid Strategy 92%] [📝 Content Brief 95%] │ │
│  │  [🎨 Creative Opt 89%] [📊 Market Analysis 94%]              │ │
│  │  [🎯 Orchestration 97%]                                        │ │
│  │                                                              │ │
│  │ Current: Bid Strategy (92% accuracy, 450ms latency)          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Model Selection with Cost                                        │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Select Model:                                               │ │
│  │  [GPT-4 $0.01/1K] [GPT-4 Turbo $0.003/1K]                     │ │
│  │  [GPT-3.5 Turbo $0.001/1K] [GPT-4 Omni $0.015/1K]            │ │
│  │                                                              │
│  │ Current: GPT-4 (Cost: £0.01/1K tokens)                       │
│  │ Session Cost: £0.75  Total Cost: £12.50                       │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Enhanced Chat History                                           │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  💬 Conversation History (chat_456)                         │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  You: What's the optimal bid for gymshark leggings?         │ │
│  │  21:04:19  🤖 Bid Strategy (GPT-4):                        │ │
│  │     Based on current market conditions, I recommend a bid   │ │
│  │     of £2.75 for phrase match. The competition is moderate  │ │
│  │     and conversion rate is 3.5%.                           │ │
│  │     Confidence: 0.85  Tokens: 150  Cost: £0.0015  Latency: 450ms│ │
│  │     Context: Summer Training Collection, ROAS 4.2             │ │
│  │     [📊 View Reasoning]  [✓ Accept]  [✗ Reject]              │ │
│  │                                                              │ │
│  │  You: Generate content brief for summer collection         │ │
│  │  21:03:45  🤝 Content Brief (GPT-4):                        │ │
│  │     Creating brief for Summer 2025...                       │ │
│  │     Topic: Seamless Leggings Launch                          │ │
│  │     Angle: Performance fabric meets summer comfort          │ │
│  │     Hook: "Experience the leggings that move with you"      │ │
│  │     Differentiation: 0.82  Confidence: 0.92                   │ │
│  │     Tokens: 280  Cost: £0.0028  Latency: 620ms               │ │
│  │     [📄 View Brief]  [✓ Accept]  [✗ Reject]  [🔄 Regenerate]  │ │
│  │                                                              │ │
│  │  You: How are campaigns performing?                         │ │
│  │  21:02:12  📊 Market Analysis (GPT-4):                      │ │
│  │     Overall ROAS is 3.25, up 55% from baseline. Top         │ │
│  │     performer is Summer Training with ROAS of 4.2.          │ │
│  │     Recent optimization: Bid increased £2.20→£2.75          │
│  │     Impact: ROAS +5%, Win Rate +8%                           │ │
│  │     Tokens: 195  Cost: £0.0019  Latency: 520ms               │ │
│  │     [📈 View Charts]  [✓ Accept]  [🔄 Ask Follow-up]          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Type your message...]  [📎 Attach File]  [🎤 Voice Input]  [Send]│ │
└─────────────────────────────────────────────────────────────────┘
```

### New Chat Features

**1. Context Awareness**
- Automatically includes current campaign, strategy, and recent optimizations
- User can add custom context notes
- Context persists across conversation

**2. Agent Performance Display**
- Shows accuracy percentage and latency for each agent
- Helps user choose best agent for task

**3. Model Cost Tracking**
- Shows cost per 1K tokens for each model
- Tracks session and total cost
- Helps with cost optimization

**4. Action Buttons on Responses**
- Accept/Reject agent recommendations
- View detailed reasoning
- Regenerate response
- Ask follow-up questions

**5. File Attachments**
- Upload files for context (CSV, images, documents)
- Agent can analyze and incorporate into responses

**6. Voice Input**
- Voice-to-text for hands-free operation
- Useful for quick queries while multitasking

---

## Page 5: Enhanced Analytics Dashboard

### Additional Metrics
```
┌─────────────────────────────────────────────────────────────────┐
│  ANALYTICS                                      [Last 12 Months ▼]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Advanced Performance Metrics                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Platform Performance Comparison                               │ │
│  │ Platform    Spend    Revenue   ROAS    CPA    Win Rate      │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Meta       £12,500   £52,500   4.20    £28    78%           │ │
│  │ Google     £10,800   £45,360   4.20    £21    82%           │ │
│  │ TikTok     £8,200    £24,600   3.00    £22    65%           │ │
│  │ Microsoft  £7,500    £30,000   4.00    £27    71%           │
│  │                                                              │ │
│  │ Total      £39,000   £152,460  3.91    £25    74%           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Model Performance Over Time                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Model               Accuracy Trend (6 months)                 │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ Bid Strategy        [88% → 90% → 89% → 91% → 92% → 92%]      │ │
│  │ Content Brief       [82% → 85% → 87% → 88% → 90% → 90%]      │ │
│  │ Creative Opt        [80% → 82% → 84% → 85% → 87% → 85%]      │ │
│  │ Market Analysis     [83% → 85% → 87% → 88% → 90% → 94%]      │ │
│  │                                                              │ │
│  │ [View Detailed Accuracy Charts]                               │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Overmind Optimization Impact                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Total Optimizations Applied: 15                              │ │
│  │ Average Impact per Optimization: +12% ROAS                  │ │
│  │ Success Rate of Optimizations: 87%                          │ │
│  │                                                              │ │
│  │ By Category:                                                 │ │
│  │ Decision Rules: 5  Average Impact: +8%                       │ │
│  │ Edge Cases: 4  Average Impact: +15%                          │ │
│  │ Quality Expectations: 3  Average Impact: +18%                │ │
│  │ Confidence Scoring: 3  Average Impact: +12%                   │ │
│  │                                                              │ │
│  │ [View All Optimizations]  [Optimization ROI Analysis]         │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Page 6: Enhanced Keyword Intelligence

### Additional Metrics
```
┌─────────────────────────────────────────────────────────────────┐
│  KEYWORD INTELLIGENCE                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Keyword Performance Heatmap                                     │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Performance by Category and Intent (30 Days)                  │ │
│  │                                                              │ │
│  │              Transactional     Informational                 │ │
│  │            ┌─────────────┬─────────────┐                      │ │
│  │  H (High)   │ ROAS 4.2   │ ROAS 3.1   │  ← Best performer     │ │
│  │            │ CPA £18     │ CPA £22     │                      │ │
│  │            │ Conv 3.8%   │ Conv 2.5%   │                      │ │
│  │  E (Guid)   │ ROAS 3.5   │ ROAS 2.8   │                      │ │
│  │            │ CPA £23     │ CPA £26     │                      │ │
│  │            │ Conv 3.2%   │ Conv 2.1%   │                      │ │
│  │  L (Other)   │ ROAS 2.8   │ ROAS 2.2   │                      │ │
│  │            │ CPA £26     │ CPA £29     │                      │ │
│  │            │ Conv 2.8%   │ Conv 1.9%   │                      │ │
│  │                                                              │ │
│  │  [View Detailed Heatmap]  [Export Data]                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Bid Optimization History                                         │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ Keyword: gymshark leggings (H)                               │ │
│  │                                                              │ │
│  │ Date        Bid     Reason                        Impact      │ │
│  │ 2025-11-23  £2.20   Initial bid                  -           │ │
│  │ 2025-11-24  £2.25   Market analysis +5% demand    +3% ROAS    │ │
│  │ 2025-11-25  £2.50   Competitor bid increase       +5% ROAS    │ │
│  │ 2025-11-26  £2.75   DisBERT intent +15% (Overmind) +5% ROAS   │ │
│  │ 2025-11-27  £2.75   Stable performance            -           │ │
│  │                                                              │ │
│  │ Total Impact: +18% ROAS, -8% CPA                             │ │
│  │                                                              │ │
│  │ [View All Bid History]  [Export to CSV]                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## New Page: Strategy Documentation Hub

```
┌─────────────────────────────────────────────────────────────────┐
│  STRATEGY DOCUMENTATION HUB                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Active Strategies                                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ 📋 Summer Performance Push                                   │ │
│  │    Status: ✅ Active  Days: 14  ROI: +28%                    │ │
│  │    [View Details]  [Edit]  [Pause]  [Archive]                │ │
│  │                                                              │ │
│  │ 📋 Fall Awareness Campaign                                     │ │
│  │    Status: ⏸️ Paused  Days: 30  ROI: +15%                    │ │
│  │    [View Details]  [Edit]  [Resume]  [Archive]               │ │
│  │                                                              │ │
│  │ 📋 Winter Holiday Push                                        │ │
│  │    Status: 📅 Scheduled  Start: 2025-12-01  ROI Target: +35% │ │
│  │    [View Details]  [Edit]  [Delete]                          │ │
│  │                                                              │ │
│  │ [+ Create New Strategy]                                       │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Strategy Performance Timeline                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  [📈 Timeline Chart]                                         │ │
│  │                                                              │ │
│  │  Summer Push Strategy Timeline:                               │ │
│  │  Nov 14: Strategy Created                                       │ │
│  │  Nov 15: Implementation Started                                 │ │
│  │  Nov 18: Overmind Opt #1 (Bid +15%) ← Impact +5% ROAS      │ │
│  │  Nov 19: Overmind Opt #2 (Creative Rotation) ← Impact +18% CTR │ │
│  │  Nov 21: Overmind Opt #3 (Geo Expansion) ← Impact +35% Leads │ │
│  │  Nov 25: Policy Calibration ← Impact +8% Confidence          │ │
│  │  Current: Day 14 of implementation                           │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Overmind Optimization History                                    │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Total Optimizations: 15  Applied: 15  Pending: 0  Rejected: 0  │ │
│  │                                                              │ │
│  │ By Agent:                                                     │ │
│  │  Bid Strategy: 5  Content Brief: 3  Creative Opt: 3          │ │
│  │  Market Analysis: 2  Orchestration: 2                          │ │
│  │                                                              │ │
│  │ By Type:                                                      │ │
│  │  Decision Rules: 5  Edge Cases: 4  Quality Exp: 3           │ │
│  │  Confidence Scoring: 3                                        │ │
│  │                                                              │ │
│  │ [View All Optimizations]  [Optimization ROI Report]         │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Enhanced Chat Features

### 1. Multi-Turn Context
```javascript
// Chat maintains context across turns
{
  "conversation_id": "chat_456",
  "context": {
    "campaign": "Summer Training Collection",
    "strategy": "Summer Performance Push",
    "recent_optimizations": [
      {
        "date": "2025-11-26",
        "type": "bid_increase",
        "details": "£2.50→£2.75",
        "impact": "+5% ROAS"
      }
    ]
  }
}
```

### 2. Agent Handoff
```javascript
// Seamless handoff between agents
User: "What's the optimal bid?"
Agent: Bid Strategy → [View Details]

User: "Now generate a creative brief"
Agent: Content Brief → [View Brief]

// Context is preserved across handoffs
```

### 3. Cost Optimization
```javascript
// Automatic model selection based on task complexity
Simple query → GPT-3.5 Turbo (cheaper)
Complex analysis → GPT-4 (more accurate)
Real-time decision → GPT-4 Turbo (balanced)

// Shows cost comparison before sending
Estimated cost with GPT-4: £0.0015
Estimated cost with GPT-3.5: £0.0003
[Use GPT-3.5] [Use GPT-4]
```

### 4. Response Actions
```javascript
// Each response has actionable buttons
{
  "response": "Recommended bid: £2.75",
  "actions": [
    {
      "type": "accept",
      "label": "Accept",
      "action": "apply_bid_change"
    },
    {
      "type": "reject",
      "label": "Reject",
      "action": "keep_current_bid"
    },
    {
      "type": "regenerate",
      "label": "Regenerate",
      "action": "get_alternative_suggestion"
    },
    {
      "type": "followup",
      "label": "Ask Follow-up",
      "action": "generate_followup_question"
    }
  ]
}
```

---

## API Endpoints for New Features

### Strategy Documentation
```python
GET /api/v1/strategies/active
GET /api/v1/strategies/{strategy_id}
POST /api/v1/strategies/create
PUT /api/v1/strategies/{strategy_id}/update
GET /api/v1/strategies/{strategy_id}/performance
GET /api/v1/strategies/{strategy_id}/optimizations
```

### Enhanced Chat
```python
POST /api/v1/chat/send-message-with-context
POST /api/v1/chat/attach-file
POST /api/v1/chat/voice-input
POST /api/v1/chat/switch-context
GET /api/v1/chat/cost-tracking
```

### Overmind Optimization Tracking
```python
GET /api/v1/optimizations/history
GET /api/v1/optimizations/{optimization_id}
GET /api/v1/optimizations/impact-report
GET /api/v1/optimizations/roi-analysis
```

---

## Summary of Enhancements

### 1. More Metrics
- Platform performance comparison table
- Model accuracy trends over time
- Keyword performance heatmap
- Bid optimization history
- Agent performance with token/cost tracking

### 2. Strategy Documentation
- Hover/click-through strategy details
- Strategy implementation tracking
- Performance since strategy (before/after comparison)
- Document management (create, edit, pause, archive)

### 3. Overmind Optimization Tracking
- Shows all optimizations applied
- Displays impact of each optimization
- Tracks optimization success rate
- Shows optimization ROI analysis
- Links to policy changes

### 4. Enhanced Chat
- Context awareness with current campaign/strategy
- Agent performance display (accuracy, latency)
- Model cost tracking and optimization
- Action buttons on responses (accept/reject/regenerate)
- File attachments
- Voice input
- Multi-turn context preservation
- Agent handoff with context preservation

The UI now comprehensively reflects all backend business logic with rich metrics and actionable insights! 🚀