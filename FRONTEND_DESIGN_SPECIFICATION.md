# SIGNAL Platform - Frontend Design Specification

**Version**: 1.0
**Date**: 2025-11-28
**Based on**: Complete Backend Implementation

---

## Table of Contents
1. [Overview](#overview)
2. [Navigation Structure](#navigation-structure)
3. [Page Designs](#page-designs)
4. [Component Library](#component-library)
5. [Color Scheme](#color-scheme)
6. [Responsive Design](#responsive-design)
7. [API Integration](#api-integration)
8. [Technical Stack](#technical-stack)

---

## Overview

The SIGNAL Platform frontend is designed as a professional Bloomberg Terminal-style dashboard that showcases all backend capabilities including:

- **5 AI Agents** with real-time signals and execution logs
- **Media Planning** with Tavily research and keyword management
- **BERT/DisBERT Classification** with keyword intelligence
- **Historical Analytics** with 12 months of performance data
- **A/B Testing** with statistical significance tracking
- **Multi-Agent Chat** with model selection
- **Campaign Keyword Logging** with Thrad data generation

---

## Navigation Structure

```
SIGNAL
├── 📊 Terminal (Bloomberg Terminal Dashboard)
├── 📈 Analytics
│   ├── Campaign Performance
│   ├── Model Accuracy
│   ├── Keyword Performance
│   └── A/B Tests
├── 🎯 Media Planning
│   ├── Tavily Research
│   ├── Keyword Management
│   ├── Campaign Logs
│   └── Thrad Data
├── 🤖 Agents
│   ├── Agent Status
│   ├── Execution History
│   └── Agent Policies
├── 💬 AI Chat
│   ├── Conversations
│   ├── Model Selection
│   └── Agent Selection
├── 🔍 Intelligence
│   ├── Reddit Insights
│   ├── SEO Keywords
│   ├── Google Bidding
│   └── Content Ideas
└── ⚙️ Settings
    ├── API Keys
    ├── Configuration
    └── Data Management
```

---

## Page Designs

### 1. Bloomberg Terminal Dashboard (Main View)

**Purpose**: Real-time monitoring of agent signals, campaign performance, and market data

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  SIGNAL TERMINAL                    GYMSHARK │ │  🔄  ⚙️      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │  AGENT SIGNALS  │  │  CAMPAIGN P&L   │  │  MARKET DATA   │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ ⚡ BUY          │  │ ROAS: 3.25     │  │ Vol: +12%      │ │
│  │ Summer Training │  │ CPL: £28       │  │ Trend: ↑       │ │
│  │ £2,500 (85%)    │  │ Rev: £42K/wk   │  │ Sent: Bullish  │ │
│  │                 │  │                 │  │                │ │
│  │ ⏸️ HOLD         │  │ Budget: £18K   │  │                │ │
│  │ Performance Gear│  │ Spent: £12.5K  │  │                │ │
│  │ £1,800 (72%)    │  │ Remaining: £5.5K│ │                │ │
│  │                 │  │                 │  │                │ │
│  │ 🛑 STOP         │  │                │  │                │ │
│  │ Old Campaign    │  │                │  │                │ │
│  │ £0 (0%)         │  │                │  │                │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  AGENT EXECUTION LOG                                    ▼   │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │ 21:04:19 [THOMPSON_ALLOCATOR] BUY Summer Training £2,500   │ │
│  │ 21:03:45 [BID_STRATEGY] Optimized bid for gymshark leggings│ │
│  │ 21:02:12 [CREATIVE_OPT] Selected video creative variant B  │ │
│  │ 21:01:33 [MARKET_ANALYSIS] Detected +15% trending interest │ │
│  │ 21:00:45 [ORCHESTRATION] Coordinated workflow update       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Components**:
- **Agent Signals Panel**: Real-time BUY/HOLD/STOP signals with confidence scores
- **Campaign P&L Panel**: ROAS, CPL, Revenue, Budget tracking
- **Market Data Panel**: Volume, trends, sentiment
- **Agent Execution Log**: Scrolling log of agent actions with timestamps

**API Endpoints**:
- `GET /api/v1/terminal/agent-signals`
- `GET /api/v1/terminal/campaign-pnl`
- `GET /api/v1/terminal/market-data`
- `GET /api/v1/terminal/agent-logs`

---

### 2. Media Planning Dashboard

**Purpose**: Tavily research integration, keyword management, and campaign logging

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  MEDIA PLANNING                                    [Research] │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  TAVILY RESEARCH                                            │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  Query: [Gymshark fitness apparel]  [🔍 Research]          │ │
│  │                                                              │ │
│  │  Reddit Posts: 15  │  SEO Keywords: 45  │  Google Kws: 30  │ │
│  │                                                              │ │
│  │  Top Reddit Insights:                                       │ │
│  │  • "Gymshark seamless leggings best for summer" (245 up)   │ │
│  │  • "Summer collection worth the hype?" (178 up)            │ │
│  │                                                              │ │
│  │  Google Keywords for Bidding:                               │ │
│  │  Keyword              Match  Bid    Intent   Category      │ │
│  │  gymshark leggings    phrase £2.75  trans    H (thrad_disbert)│ │
│  │  buy gymshark online  exact  £3.50  trans    H (thrad_disbert)│ │
│  │  gym wear women       broad  £2.20  info     E (thrad_disbert)│ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  CAMPAIGN KEYWORD LOGS                                      │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  Campaign: GYMSHARK_PPC_GENERIC_2026  Model: thrad_disbert │ │
│  │                                                              │ │
│  │  Keyword              Match  Bid    Source    Logged        │ │
│  │  gymshark leggings    phrase £2.75  tavily    2 min ago    │ │
│  │  buy gym clothes      exact  £3.20  tavily    2 min ago    │ │
│  │  fitness workout      broad  £1.85  bert      5 min ago    │ │
│  │                                                              │ │
│  │  [📊 View Thrad Data]  [📤 Export Logs]                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Components**:
- **Tavily Research Panel**: Query input, Reddit insights, SEO keywords, Google keywords
- **Campaign Keyword Logs**: Table of logged keywords with DisBERT model specification
- **Thrad Data Viewer**: Modal to view conversation context and user metadata

**API Endpoints**:
- `POST /api/v1/intelligence/gymshark-research`
- `GET /api/v1/intelligence/gymshark-reddit`
- `GET /api/v1/intelligence/gymshark-google-keywords`
- `GET /api/v1/planning/campaign-keyword-logs`
- `POST /api/v1/planning/complete-planning-with-keywords`

---

### 3. Agent Management

**Purpose**: Monitor 5 AI agents, view status, execution history, and policies

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  AGENT MANAGEMENT                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ BID STRATEGY    │  │ CONTENT BRIEF  │  │ CREATIVE OPT    │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ Status: ✅ Active│  │ Status: ✅ Active│  │ Status: ✅ Active│ │
│  │ Executions: 750  │  │ Executions: 720  │  │ Executions: 680  │ │
│  │ Success: 92%     │  │ Success: 95%     │  │ Success: 89%     │ │
│  │ Latency: 450ms  │  │ Latency: 620ms  │  │ Latency: 380ms  │ │
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
│  │                 │  │                 │                       │
│  │ [View Policy]   │  │ [View Policy]   │                       │
│  │ [View History]  │  │ [View History]  │                       │
│  └─────────────────┘  └─────────────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

**Components**:
- **Agent Cards**: Status, execution count, success rate, latency
- **Policy Viewer**: Modal to view agent policy files
- **History Viewer**: Detailed execution history with inputs/outputs

**API Endpoints**:
- `GET /api/v1/agents/status`
- `GET /api/v1/agents/execution-history`
- `GET /api/v1/agents/policy/{agent_name}`

---

### 4. LLM Chat Interface

**Purpose**: Multi-agent chat with model selection and conversation history

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  AI CHAT                                         [GPT-4 ▼]      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  Select Agent:                                              │ │
│  │  [🤖 General] [💰 Bid Strategy] [📝 Content Brief]         │ │
│  │  [🎨 Creative Opt] [📊 Market Analysis] [🎯 Orchestration] │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  💬 Conversation History                                    │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  You: What's the optimal bid for gymshark leggings?         │ │
│  │  🤖 Bid Strategy: Based on current market conditions,      │ │
│  │     I recommend a bid of £2.75 for phrase match. The      │ │
│  │     competition is moderate and conversion rate is 3.5%.  │ │
│  │                                                              │ │
│  │  You: Generate content brief for summer collection         │ │
│  │  🤝 Content Brief: Creating brief for Summer 2025...       │ │
│  │     Focus on seamless leggings, performance fabric,       │ │
│  │     targeting 18-34 fitness enthusiasts.                   │ │
│  │                                                              │ │
│  │  You: How are campaigns performing?                         │ │
│  │  📊 Market Analysis: Overall ROAS is 3.25, up 55% from     │ │
│  │     baseline. Top performer is Summer Training with       │ │
│  │     ROAS of 4.2.                                            │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  [Type your message...]                                    [Send] │
└─────────────────────────────────────────────────────────────────┘
```

**Components**:
- **Model Selector**: Dropdown to choose model (GPT-4, GPT-4 Turbo, GPT-3.5, GPT-4 Omni)
- **Agent Selector**: Buttons to choose specialized agent
- **Conversation History**: Scrollable chat interface with message bubbles
- **Message Input**: Text input with send button

**API Endpoints**:
- `POST /api/v1/chat/send-message`
- `GET /api/v1/chat/list-agents`
- `GET /api/v1/chat/list-models`
- `GET /api/v1/chat/conversations/{chat_id}`

---

### 5. Analytics Dashboard

**Purpose**: Historical performance visualization with 12 months of data

**Layout**:
```
┌─────────────────────────────────────────────────────────────────┐
│  ANALYTICS                                      [Last 12 Months ▼]│
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  HISTORICAL CAMPAIGN PERFORMANCE                            │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  [📈 ROAS Trend Chart]                                      │ │
│  │  4.5 ┤     ╭────╮                                           │ │
│  │  4.0 ┤   ╭─╯    ╰─╮                                         │ │
│  │  3.5 ┤ ╭─╯         ╰─╮                                       │ │
│  │  3.0 ┤─╯             ╰───╮                                   │ │
│  │  2.5 ┤                    ╰─╮                                 │ │
│  │      └─────────────────────────╮─────────────────────       │ │
│  │        Jun Jul Aug Sep Oct Nov Dec Jan Feb Mar Apr May      │ │
│  │                                                              │ │
│  │  Summer 2024: 2.1  Fall 2024: 2.8  Winter 2025: 3.1      │ │
│  │  Spring 2025: 3.8  Current: 4.2                             │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ MODEL ACCURACY  │  │ KEYWORD PERF   │  │ A/B TESTS       │ │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────┤ │
│  │ Bid Strategy:   │  │ Top Keywords:   │  │ Creative Test:  │ │
│  │ 92% accuracy    │  │ gymshark leggs  │  │ Winner: Video   │ │
│  │                 │  │ ROAS: 4.5      │  │ Confidence: 92% │ │
│  │ Keyword Class:  │  │ buy gym clothes │  │                 │ │
│  │ 88% accuracy    │  │ ROAS: 3.8      │  │ Bid Test:       │ │
│  │                 │  │                 │  │ Winner: Auto    │ │
│  │ Creative Opt:   │  │ fitness workout │  │ Confidence: 88% │ │
│  │ 85% accuracy    │  │ ROAS: 2.9      │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Components**:
- **Historical Chart**: ROAS trend over 12 months with seasonal annotations
- **Model Accuracy Panel**: Accuracy metrics for each model
- **Keyword Performance Panel**: Top performing keywords with ROAS
- **A/B Tests Panel**: Test results with winners and confidence

**API Endpoints**:
- `GET /api/v1/analytics/historical-performance`
- `GET /api/v1/analytics/model-accuracy`
- `GET /api/v1/analytics/keyword-performance`
- `GET /api/v1/analytics/ab-test-results`

---

### 6. Keyword Intelligence

**Purpose**: DisBERT classification, keyword performance, and Thrad data visualization

**Layout**:
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
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  KEYWORD PERFORMANCE (30 Days)                              │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  Keyword              Impressions  Clicks  Conv   CPA   ROAS│ │
│  │  gymshark leggings    125,000      3,750   150    £18   4.2│ │
│  │  buy gym clothes       98,000      2,940   125    £20   3.8│ │
│  │  fitness workout       85,000      2,550    95    £22   3.4│ │
│  │  seamless leggings    110,000      3,300   140    £19   4.0│ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │  THRAD DATA                                                  │ │
│  ├─────────────────────────────────────────────────────────────┤ │
│  │  User: user_123  Chat: chat_456                            │ │
│  │  Summary: User interested in gymshark leggings              │ │
│  │  Model: thrad_disbert                                       │ │
│  │  Config: ad_offset=3, max_freq=5, experiment=variant_a      │ │
│  │  Messages: 4  Turns: 4  Ad Formats: sponsored, banner      │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Components**:
- **DisBERT Classification Panel**: Query input, category, intent, keyword strategy
- **Keyword Performance Table**: Impressions, clicks, conversions, CPA, ROAS
- **Thrad Data Panel**: User metadata, conversation summary, config, messages

**API Endpoints**:
- `POST /api/v1/intelligence/classify-keyword`
- `GET /api/v1/analytics/keyword-performance`
- `GET /api/v1/planning/keyword-logs-by-source`

---

## Component Library

### 1. Agent Signal Card
```
┌─────────────────┐
│ ⚡ BUY          │
│ Summer Training │
│ £2,500 (85%)    │
└─────────────────┘
```

**States**: BUY (green), HOLD (yellow), STOP (red)

### 2. Metric Card
```
┌─────────────────┐
│ ROAS: 3.25     │
│ +55% vs baseline│
└─────────────────┘
```

### 3. Agent Card
```
┌─────────────────┐
│ BID STRATEGY    │
│ Status: ✅ Active│
│ Executions: 750  │
│ Success: 92%     │
│ Latency: 450ms  │
│                 │
│ [View Policy]   │
└─────────────────┘
```

### 4. Chat Message Bubble
```
┌─────────────────────────────────┐
│ 🤖 Bid Strategy                │
│ Based on current market...     │
│ I recommend a bid of £2.75...  │
└─────────────────────────────────┘
```

### 5. Data Table
```
┌─────────────────────────────────────────────────────────────┐
│ Keyword         Match  Bid    Intent   Category           │
├─────────────────────────────────────────────────────────────┤
│ gymshark leggs  phrase £2.75  trans    H (thrad_disbert)  │
│ buy gym clothes  exact  £3.50  trans    H (thrad_disbert)  │
└─────────────────────────────────────────────────────────────┘
```

---

## Color Scheme

### Bloomberg Terminal Theme (Dark Mode)

**Background Colors**:
- Primary Background: `#1a1a1a` (Dark Gray)
- Secondary Background: `#2a2a2a` (Lighter Gray)
- Card Background: `#3a3a3a` (Medium Gray)
- Input Background: `#4a4a4a` (Light Gray)

**Text Colors**:
- Primary Text: `#ffffff` (White)
- Secondary Text: `#cccccc` (Light Gray)
- Muted Text: `#888888` (Gray)
- Accent Text: `#00bfff` (Blue)

**Signal Colors**:
- BUY Signal: `#00ff00` (Green)
- HOLD Signal: `#ffff00` (Yellow)
- STOP Signal: `#ff0000` (Red)

**Status Colors**:
- Success: `#00ff00` (Green)
- Warning: `#ffff00` (Yellow)
- Error: `#ff0000` (Red)
- Info: `#00bfff` (Blue)

**Chart Colors**:
- Line 1: `#00bfff` (Blue)
- Line 2: `#00ff00` (Green)
- Line 3: `#ffff00` (Yellow)
- Line 4: `#ff00ff` (Magenta)
- Line 5: `#00ffff` (Cyan)

---

## Responsive Design

### Desktop (1920px+)
- Full Bloomberg Terminal experience
- 3-column layout for agent cards
- Full-width charts
- Side navigation

### Tablet (768px - 1919px)
- Simplified dashboard with key metrics
- 2-column layout for agent cards
- Stacked panels
- Bottom navigation

### Mobile (< 768px)
- Agent signals only
- Chat interface
- Single column layout
- Hamburger menu

---

## API Integration

### Authentication
- JWT token in header
- Refresh token mechanism
- Role-based access control

### Real-time Updates
- WebSocket connections for:
  - Agent signals
  - Campaign performance
  - Execution logs
- Polling fallback (30 seconds)

### Data Fetching
- React Query / SWR for caching
- Optimistic updates
- Error boundary handling
- Loading states

### Error Handling
- Toast notifications
- Error modal for critical failures
- Retry mechanism with exponential backoff
- Offline mode support

---

## Technical Stack

### Frontend Framework
- **React 18** with TypeScript
- **Next.js 14** (App Router)
- **Vite** for build tooling

### UI Components
- **Tailwind CSS** for styling
- **shadcn/ui** for component library
- **Recharts** for charts
- **Framer Motion** for animations

### State Management
- **Zustand** for global state
- **React Context** for theme/auth
- **TanStack Query** for server state

### Real-time
- **Socket.io** for WebSocket
- **Pusher** as fallback

### Charts & Visualization
- **Recharts** for line/bar charts
- **D3.js** for complex visualizations
- **Victory** for statistical charts

### Forms & Validation
- **React Hook Form**
- **Zod** for schema validation
- **Yup** for additional validation

### Testing
- **Jest** for unit tests
- **React Testing Library** for component tests
- **Playwright** for E2E tests
- **Cypress** as alternative E2E

### Build & Deploy
- **Vite** for build optimization
- **Docker** for containerization
- **Vercel/Netlify** for deployment
- **GitHub Actions** for CI/CD

---

## Performance Optimizations

### Code Splitting
- Route-based splitting
- Component lazy loading
- Dynamic imports

### Caching
- Service worker for offline
- Local storage for preferences
- Session storage for temporary data

### Bundle Size
- Tree shaking
- Minification
- Gzip compression
- Image optimization

### Loading States
- Skeleton screens
- Progressive loading
- Infinite scroll for logs

---

## Accessibility

### WCAG 2.1 AA Compliance
- Keyboard navigation
- Screen reader support
- ARIA labels
- Focus management

### Color Contrast
- Minimum 4.5:1 ratio
- Color-blind friendly palette
- Text alternatives for charts

### Responsive Text
- Scalable font sizes
- Readable line lengths
- Proper heading hierarchy

---

## Internationalization

### Supported Languages
- English (en) - Primary
- Spanish (es)
- German (de)
- French (fr)

### Date/Time Formatting
- Locale-aware dates
- Time zone support
- Relative time formatting

### Currency Formatting
- GBP (£) - Primary
- USD ($)
- EUR (€)

---

## Security

### Authentication
- JWT with refresh tokens
- Multi-factor authentication (MFA)
- Session timeout
- Remember me functionality

### Authorization
- Role-based access control (RBAC)
- Permission-based UI
- Audit logging

### Data Protection
- Encryption in transit (TLS)
- Encryption at rest
- Data masking for sensitive info
- GDPR compliance

---

## Future Enhancements

### Phase 2 Features
- Dark/Light theme toggle
- Customizable dashboard layouts
- Advanced filtering and sorting
- Export to CSV/PDF
- Scheduled reports

### Phase 3 Features
- Mobile app (React Native)
- Voice commands
- AI-powered insights
- Predictive analytics
- Collaboration features

---

## Conclusion

This frontend design leverages all backend capabilities including:
- ✅ 5 AI Agents with real-time signals
- ✅ Tavily Research integration
- ✅ BERT/DisBERT classification
- ✅ 12 months of historical data
- ✅ Keyword performance tracking
- ✅ A/B testing results
- ✅ Multi-agent chat
- ✅ Campaign keyword logging with Thrad data

The Bloomberg Terminal-style interface provides a professional, data-driven experience perfect for adtech professionals.