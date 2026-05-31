# SIGNAL Platform - Demo Guide

## 🎯 Demo Scenario: Acme Fashion E-commerce

This guide walks through the complete demo scenario for **Acme Fashion**, a fashion e-commerce client using the SIGNAL platform for autonomous media trading.

### Client Profile
- **Name**: Acme Fashion
- **Industry**: Fashion E-commerce
- **Business Model**: Premium sustainable fashion retailer
- **Target Audience**: Fashion-conscious millennials and Gen Z
- **Markets**: US, UK, Germany, France
- **Current Spend**: Meta ($15k/mo), Google ($12k/mo), TikTok ($9k/mo), Microsoft ($6k/mo)
- **Key Goals**: Lead generation (1000 leads/week), customer acquisition, brand awareness

---

## 🚀 Setup Instructions

### 1. Environment Setup

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
# Required: DATABASE_URL, TAVILY_API_KEY, OVERMIND_API_KEY, THRAD_API_KEY
```

### 2. Install Dependencies

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Or install core dependencies
pip install -e .
```

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head

# Populate demo data
./scripts/setup_demo.sh
```

### 4. Start the API Server

```bash
# Development mode with auto-reload
uvicorn api.main:app --reload

# Production mode
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 5. Access API Documentation

Open your browser to: `http://localhost:8000/docs`

---

## 📊 Demo User Journey

### Step 1: Client Login & Dashboard Overview

**Endpoint**: `GET /api/v1/demo/dashboard/overview?client_id=<client_id>`

**What the user sees**:
- Client profile and status
- Recent content briefs from Tavily intelligence
- Budget allocation rounds (last 4 weeks)
- Goal progress (leads, customers, revenue, awareness)
- Active campaigns summary
- Weekly budget and token balance

**Demo Script**:
```bash
# Get client ID from demo data output
CLIENT_ID="your_client_id_here"

# View dashboard overview
curl "http://localhost:8000/api/v1/demo/dashboard/overview?client_id=$CLIENT_ID"
```

**Response Highlights**:
- 3 recent content briefs (Sustainable Summer Fashion, Gen Z Micro-Trends, Back to Campus)
- 4 weeks of budget allocation history showing decay-based decisions
- Goal progress: 850/1000 leads (85%), 180/200 customers (90%)
- 4 active campaigns across Meta, Google, TikTok, Microsoft
- Token balance: ~720 tokens from rewards

---

### Step 2: Tavily Crawling & Topic Clustering

**Endpoint**: `GET /api/v1/demo/intelligence/tavily-results?client_id=<client_id>`

**What the user sees**:
- Live Tavily crawling results from social media monitoring
- Topic clusters with search volume, competition, and trend data
- Content briefs generated from intelligence
- Crawling summary with active clusters and growth rates

**Demo Script**:
```bash
# View Tavily intelligence and topic clustering
curl "http://localhost:8000/api/v1/demo/intelligence/tavily-results?client_id=$CLIENT_ID"
```

**Response Highlights**:
- **Sustainable Fashion**: 125K search volume, 23% growth rate, trending up
- **Summer Fashion Trends**: 89K search volume, 18% growth rate, trending up
- **Gen Z Fashion**: 156K search volume, 34% growth rate, trending up
- 3 content briefs with key insights from social media monitoring
- crawling summary: 62% increase in "sustainable summer fashion" searches

---

### Step 3: Topic Cluster Briefs (SEO & Geo Optimization)

**Endpoint**: `GET /api/v1/demo/intelligence/topic-clusters?client_id=<client_id>`

**What the user sees**:
- Detailed topic cluster analysis
- SEO opportunity scoring (priority, difficulty, potential traffic)
- Geo optimization breakdown by market (US, UK, Germany, France)
- Related topics and seasonal patterns

**Demo Script**:
```bash
# View topic clusters with SEO and geo optimization
curl "http://localhost:8000/api/v1/demo/intelligence/topic-clusters?client_id=$CLIENT_ID"
```

**Response Highlights**:
- **Sustainable Fashion**: High priority, low difficulty, 153K potential traffic
- **Geo breakdown**: US (40%), UK (25%), Germany (20%), France (15%)
- **Seasonal patterns**: Peak months June-August
- **Related topics**: Zero waste fashion, circular fashion, vegan fashion

---

### Step 4: CPL Output Matrix & Scenario Builder

**Endpoint**: `GET /api/v1/demo/planning/cpl-matrix?client_id=<client_id>&target_leads=1000`

**What the user sees**:
- Current CPL and performance metrics
- Scenario planning for lead targets
- Conservative, optimistic, and aggressive scenarios
- Budget requirements and expected outcomes
- Agent recommendations

**Demo Script**:
```bash
# View CPL matrix for 1000 lead target
curl "http://localhost:8000/api/v1/demo/planning/cpl-matrix?client_id=$CLIENT_ID&target_leads=1000"
```

**Response Highlights**:
- **Current CPL**: $28.00 (down 20% from $35.00 before SIGNAL)
- **Current ROAS**: 3.25 (up 55% from 2.1 before SIGNAL)
- **Conservative scenario**: $28,000 budget, 1000 leads, $91,000 revenue
- **Optimistic scenario**: $25,200 budget, 1000 leads, $99,900 revenue
- **Aggressive scenario**: $22,400 budget, 1000 leads, $108,000 revenue
- **Agent recommendation**: Optimistic scenario with 10% improvement

---

### Step 5: Custom Scenario Builder

**Endpoint**: `POST /api/v1/demo/planning/scenario-builder?client_id=<client_id>`

**What the user sees**:
- Interactive scenario builder
- Platform-specific allocation (Meta, Google, TikTok, Microsoft)
- Optimization level selection (conservative, moderate, aggressive)
- Per-platform performance assumptions
- Agent recommendations and risk factors

**Demo Script**:
```bash
# Build custom scenario
curl -X POST "http://localhost:8000/api/v1/demo/planning/scenario-builder?client_id=$CLIENT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "target_leads": 1000,
    "target_cpa": 25.0,
    "platform_allocation": {
      "meta": 0.30,
      "google": 0.30,
      "tiktok": 0.25,
      "microsoft": 0.15
    },
    "optimization_level": "moderate"
  }'
```

**Response Highlights**:
- **Total budget**: $26,250
- **Expected revenue**: $85,312
- **Overall ROAS**: 3.25
- **Platform breakdown**:
  - Meta: 300 leads, $8,400 budget, $26,880 revenue
  - Google: 300 leads, $8,640 budget, $30,240 revenue
  - TikTok: 250 leads, $4,950 budget, $13,860 revenue
  - Microsoft: 150 leads, $5,250 budget, $15,750 revenue

---

### Step 6: Agent Chat - "What Happened in the Last Two Weeks?"

**Endpoint**: `POST /api/v1/demo/agents/chat?client_id=<client_id>&message=<message>`

**What the user sees**:
- Natural language chat interface with AI agents
- Performance summary with key metrics
- Detailed insights and learnings
- Opportunities identified
- Agent contributions and Overmind evals

**Demo Script**:
```bash
# Ask agents what happened in the last two weeks
curl -X POST "http://localhost:8000/api/v1/demo/agents/chat?client_id=$CLIENT_ID&message=What%20happened%20in%20the%20last%20two%20weeks%20and%20what%20have%20you%20learned"
```

**Response Highlights**:
- **Summary**: "Since you've been working with SIGNAL, you've achieved a 20% reduction in CPL and 40% increase in leads"
- **Key metrics**: 
  - Current CPL: $28.00 (20% reduction)
  - Weekly leads: 1,120 (40% increase)
  - Current ROAS: 3.25 (55% improvement)
  - LTV:CAC: 4.1 (28% improvement)
- **Insights**: 
  - Strong sustainable fashion content driving 35% of leads
  - TikTok Gen Z campaign 4.2% engagement rate
  - Google search 45% higher conversion on sustainable keywords
- **Opportunities**: 
  - Expand successful creative to Microsoft platform
  - Increase TikTok budget for back-to-school campaign
  - Test new creative variants for summer trends
- **Learnings**: 
  - UGC creatives 2.3x better than studio content
  - Evening delivery (6-9 PM) 35% higher conversion
  - Mobile-first format resonating with audience
- **Overmind evals**: Quality score 0.92, 5 optimization cycles, 15% learning rate

---

### Step 7: Efficiency Metrics Dashboard

**Endpoint**: `GET /api/v1/demo/agents/efficiency-metrics?client_id=<client_id>`

**What the user sees**:
- Before/after comparison metrics
- Business KPI improvements (LTV:CAC, retention, cart abandonment)
- Driver analysis of improvements
- Agent quality scores and optimization cycles

**Demo Script**:
```bash
# View efficiency metrics
curl "http://localhost:8000/api/v1/demo/agents/efficiency-metrics?client_id=$CLIENT_ID"
```

**Response Highlights**:
- **CPL reduction**: 20% ($35.00 → $28.00, $7.00 savings per lead)
- **Lead increase**: 40% (800 → 1,120 leads per week, 320 additional leads)
- **ROAS improvement**: 55% (2.1 → 3.25)
- **Business KPIs**:
  - LTV:CAC: +28% (3.2 → 4.1)
  - Retention rate: +15% (68% → 78%)
  - Cart abandonment: -19% (72% → 58%)
- **Drivers**: AI bid optimization, creative optimization, strategic allocation, real-time monitoring
- **Agent quality**: 0.88 score, 5 optimization cycles, 15% learning rate

---

### Step 8: Creative Upload & Bulk Management

**Endpoint**: `POST /api/v1/demo/creatives/bulk-upload?client_id=<client_id>`

**What the user sees**:
- Bulk creative upload interface
- Multi-platform support (TikTok, Meta, Google)
- Automatic placement via MCP integrations
- Upload status and platform confirmation

**Demo Script**:
```bash
# Bulk upload creatives for TikTok and paid social
curl -X POST "http://localhost:8000/api/v1/demo/creatives/bulk-upload?client_id=$CLIENT_ID" \
  -H "Content-Type: application/json" \
  -d '[
    {
      "name": "Summer Collection Video 1",
      "type": "video",
      "format": "vertical",
      "platforms": ["tiktok"],
      "metadata": {"duration": 15, "dimensions": "1080x1920"}
    },
    {
      "name": "Summer Collection Video 2",
      "type": "video",
      "format": "vertical",
      "platforms": ["tiktok"],
      "metadata": {"duration": 20, "dimensions": "1080x1920"}
    },
    {
      "name": "Sustainable Fashion Carousel",
      "type": "carousel",
      "format": "square",
      "platforms": ["meta", "instagram"],
      "metadata": {"card_count": 5, "dimensions": "1080x1080"}
    },
    {
      "name": "Back to School Static",
      "type": "static_image",
      "format": "horizontal",
      "platforms": ["meta", "google"],
      "metadata": {"dimensions": "1200x628"}
    }
  ]'
```

**Response Highlights**:
- **Upload complete**: 4 creatives uploaded
- **MCP integrations**:
  - Meta: Active - auto-placing in feed and story placements
  - TikTok: Active - auto-placing in in-feed and top view
  - Google: Active - auto-placing in display and video
- **Creative status**: Pending review and activation

---

### Step 9: Keyword Generation (Google Ads & Microsoft)

**Endpoint**: `GET /api/v1/demo/intelligence/keywords?client_id=<client_id>&topic=<topic>&platform=<platform>`

**What the user sees**:
- Platform-specific keyword generation
- Match type recommendations (broad, phrase, exact)
- Negative keyword suggestions
- Bid suggestions based on competition
- Search volume and competition data

**Demo Script**:
```bash
# Generate keywords for Google Ads
curl "http://localhost:8000/api/v1/demo/intelligence/keywords?client_id=$CLIENT_ID&topic=sustainable%20fashion&platform=google"

# Generate keywords for Microsoft Ads
curl "http://localhost:8000/api/v1/demo/intelligence/keywords?client_id=$CLIENT_ID&topic=sustainable%20fashion&platform=microsoft"
```

**Response Highlights**:
- **Topic**: Sustainable Fashion
- **Base keywords**: sustainable fashion, eco clothing, ethical fashion, recycled materials
- **Google keywords**: 35+ variations including "sustainable fashion for sale", "buy sustainable fashion", "best sustainable fashion"
- **Microsoft keywords**: 25+ variations including "sustainable fashion shopping", "sustainable fashion store"
- **Match types**: Broad, phrase, exact recommendations
- **Negative keywords**: free, cheap, wholesale, used, second hand, repair, diy
- **Bid suggestions**: High intent $1.63, Medium intent $1.17, Low intent $0.78

---

### Step 10: Campaign Performance with Business KPIs

**Endpoint**: `GET /api/v1/demo/campaigns/performance?client_id=<client_id>`

**What the user sees**:
- Individual campaign performance metrics
- Business KPIs that matter: LTV:CAC, retention rate, cart abandonment
- Platform-specific performance
- Target audience and budget data

**Demo Script**:
```bash
# View campaign performance
curl "http://localhost:8000/api/v1/demo/campaigns/performance?client_id=$CLIENT_ID"
```

**Response Highlights**:
- **Summer Collection Launch (Meta)**: 
  - 1.5M impressions, 37.5K clicks, 1.1K conversions
  - $9,000 spend, $28,800 revenue, 3.2 ROAS
  - LTV:CAC: 4.1, Retention: 78%, Cart abandonment: 58%
- **Sustainable Fashion Campaign (Google)**:
  - 870K impressions, 30.5K clicks, 1.4K conversions
  - $7,500 spend, $26,250 revenue, 3.5 ROAS
  - LTV:CAC: 4.1, Retention: 78%, Cart abandonment: 58%
- **TikTok Trending Styles**:
  - 2.4M impressions, 96K clicks, 1.9K conversions
  - $5,100 spend, $14,280 revenue, 2.8 ROAS
  - LTV:CAC: 3.2, Retention: 68%, Cart abandonment: 72%

---

### Step 11: Business KPIs Overview

**Endpoint**: `GET /api/v1/demo/campaigns/business-kpis?client_id=<client_id>`

**What the user sees**:
- Aggregated business KPIs across all campaigns
- Agent optimization progress and goal alignment
- Adaptive behavior as business grows
- Improvement timeline

**Demo Script**:
```bash
# View business KPIs overview
curl "http://localhost:8000/api/v1/demo/campaigns/business-kpis?client_id=$CLIENT_ID"
```

**Response Highlights**:
- **Summary**: 4 campaigns, 4 active, $42K total spend, $136.5K total revenue, 3.25 ROAS
- **Business KPIs**:
  - LTV:CAC: 4.1 (target 5.0, +28% improvement, trending up)
  - Retention rate: 78% (target 85%, +15% improvement, trending up)
  - Cart abandonment: 58% (target 50%, -19% improvement, trending up)
  - Customer LTV: $233.33 (target $280.00, +18% improvement, trending up)
- **Agent optimization**:
  - "Agents have learned to optimize toward your business goals"
  - Goal alignment: Lead generation (CPL reduction), Customer acquisition (CAC reduction), Revenue (ROAS & LTV:CAC), Retention (cart abandonment)
  - "As your business grows, agents automatically adjust optimization strategies to maintain alignment with your evolving goals"

---

## 🎬 Complete Demo Flow

### Narrator Script

"Welcome to SIGNAL, the autonomous media trading platform. Let me show you how Acme Fashion, a sustainable fashion e-commerce brand, uses AI agents to optimize their advertising performance."

**[Step 1: Login & Dashboard]**
"Acme Fashion logs into their dashboard. They can see their 4 active campaigns across Meta, Google, TikTok, and Microsoft, with a weekly budget of $3,500. They're currently at 850 of their 1,000 weekly lead goal."

**[Step 2: Tavily Intelligence]**
"Let's look at what's happening in the market. SIGNAL uses Tavily to crawl social media and identify trending topics. We can see 3 key topic clusters: Sustainable Fashion with 125K searches and 23% growth, Summer Fashion Trends with 89K searches, and Gen Z Fashion with 156K searches and 34% growth."

**[Step 3: Content Briefs]**
"Based on this intelligence, SIGNAL has generated 3 content briefs for the creative team. The Sustainable Summer Fashion brief shows a 62% increase in searches and recommends bright, natural lighting with sustainability messaging."

**[Step 4: Budget Allocation]**
"Looking at the last 4 weeks of budget allocations, we can see how the decay-based Thompson sampling algorithm has adjusted spending. Week 1 was more exploratory, while recent weeks focus more on exploitation of high-performing channels like TikTok for Gen Z trends."

**[Step 5: CPL Matrix]**
"The marketing director wants to achieve 1,000 leads this week. Using the CPL output matrix, she can see different scenarios. The current CPL is $28, down 20% from $35 before using SIGNAL. An optimistic scenario with 10% improvement would require $25,200 budget to hit the target."

**[Step 6: Agent Chat]**
"Now let's ask the AI agents: 'What happened in the last two weeks and what have you learned?' The agents respond with a comprehensive summary: 'Since you've been working with SIGNAL, you've achieved a 20% reduction in CPL and 40% increase in leads.' They provide detailed insights on sustainable fashion content performance, TikTok engagement, and Google search conversions. They also identify opportunities like expanding successful creatives to Microsoft and increasing TikTok budget for back-to-school campaigns."

**[Step 7: Efficiency Metrics]**
"The efficiency dashboard shows the full impact: CPL reduced by 20%, leads increased by 40%, ROAS improved by 55%, and business KPIs like LTV:CAC improved by 28%, retention rate by 15%, and cart abandonment reduced by 19%."

**[Step 8: Creative Upload]**
"The marketing team uploads 4 new creatives - 2 TikTok videos for the summer collection, a sustainable fashion carousel for Meta and Instagram, and a back-to-school static image. Through MCP integrations, these are automatically placed in the optimal positions across platforms."

**[Step 9: Keywords]**
"For Google and Microsoft campaigns, SIGNAL generates platform-specific keywords based on the Sustainable Fashion topic cluster. It provides 35+ keyword variations, match type recommendations, negative keywords, and bid suggestions based on competition."

**[Step 10: Campaign Performance]**
"Looking at individual campaign performance, the Summer Collection Launch on Meta has 3.2 ROAS with strong business KPIs, while the TikTok Trending Styles campaign shows 2.8 ROAS with high engagement."

**[Step 11: Business KPIs]**
"Finally, the business KPIs overview shows that agents are learning to optimize toward Acme's specific goals. As the business grows, agents automatically adjust strategies to maintain alignment with evolving goals like lead generation, customer acquisition, revenue growth, and retention improvement."

**[Closing]**
"This is SIGNAL - autonomous media trading powered by AI agents, with Overmind tracing and optimization, Thrad multi-bidder auction integration, and a comprehensive attention token economy. The system continuously learns and adapts to deliver measurable business results."

---

## 🔧 API Endpoint Reference

### Dashboard Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/demo/dashboard/overview` | Main dashboard overview |
| GET | `/api/v1/demo/dashboard/briefs` | Content briefs list |
| GET | `/api/v1/demo/dashboard/allocations` | Budget allocation history |

### Intelligence Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/demo/intelligence/tavily-results` | Tavily crawling results |
| GET | `/api/v1/demo/intelligence/topic-clusters` | Topic clusters with SEO/geo |
| GET | `/api/v1/demo/intelligence/keywords` | Keyword generation |

### Planning Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/demo/planning/cpl-matrix` | CPL output matrix |
| POST | `/api/v1/demo/planning/scenario-builder` | Custom scenario builder |

### Agent Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/demo/agents/chat` | Agent chat interface |
| GET | `/api/v1/demo/agents/efficiency-metrics` | Efficiency metrics |

### Creative Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/demo/creatives` | List creatives |
| POST | `/api/v1/demo/creatives/upload` | Upload single creative |
| POST | `/api/v1/demo/creatives/bulk-upload` | Bulk upload creatives |

### Campaign Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/demo/campaigns/performance` | Campaign performance |
| GET | `/api/v1/demo/campaigns/business-kpis` | Business KPIs overview |

---

## 🎯 Hackathon Evaluation Points

### Thrad AI Integration ✅
- Direct integration with Thrad's paid LLM API for multi-bidder auctions
- Strategic agent recommendations enhance Thrad configuration
- Real-time ad serving with proven auction infrastructure

### Overmind Integration ✅
- Agent tracing for all strategic recommendations
- Quality scoring (0.92) and optimization cycles (5)
- Learning rate (15%) with continuous improvement
- Performance evals and feedback loops

### Technical Excellence ✅
- Comprehensive API with 15+ demo endpoints
- Realistic demo data with 60 days of performance history
- Business KPIs that matter (LTV:CAC, retention, cart abandonment)
- MCP integrations for automated creative placement
- Topic clustering with SEO and geo optimization
- Scenario builder for what-if analysis
- Agent chat interface with natural language understanding

---

## 🚀 Quick Start Commands

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your API keys

# 2. Install dependencies
pip install -e ".[dev]"

# 3. Setup database
alembic upgrade head

# 4. Populate demo data
./scripts/setup_demo.sh

# 5. Start API server
uvicorn api.main:app --reload

# 6. Test endpoints
curl "http://localhost:8000/health"
curl "http://localhost:8000/api/v1/demo/dashboard/overview?client_id=<client_id>"
```

---

## 📱 Demo Tips

1. **Use the interactive API docs**: Visit `http://localhost:8000/docs` for a Swagger UI interface
2. **Test with curl or Postman**: All endpoints are fully functional with demo data
3. **Customize scenarios**: Use the scenario builder to test different allocation strategies
4. **Chat with agents**: Try different questions like "What are my top performing campaigns?" or "Recommend budget allocation"
5. **Explore topic clusters**: Check different topics for keyword generation
6. **Monitor efficiency**: Track how efficiency metrics improve over time

---

## 🎨 Customization

### Adding Your Own Client Data

Edit `scripts/demo_data.py` to customize:
- Client profile and industry
- Campaign details and budgets
- Performance metrics and history
- Content briefs and topic clusters
- Creative assets and placements

### Adjusting Performance Metrics

Modify the efficiency metrics in the demo data script to show different improvement scenarios.

### Adding New API Endpoints

Add new endpoints to `api/routes/demo.py` following the existing patterns.

---

## 🐛 Troubleshooting

### Database Connection Issues
- Ensure DATABASE_URL is correctly set in .env
- Run `alembic upgrade head` to create tables
- Check PostgreSQL is running

### API Key Issues
- Verify TAVILY_API_KEY, OVERMIND_API_KEY, THRAD_API_KEY in .env
- Check API keys are valid and have required permissions

### Demo Data Issues
- Run `./scripts/setup_demo.sh` to repopulate data
- Check for existing client data (script will skip if client exists)

### Port Already in Use
- Change port: `uvicorn api.main:app --port 8001`
- Kill existing process: `lsof -ti:8000 | xargs kill`

---

## 📞 Support

For issues or questions:
- Check the API documentation at `/docs`
- Review the main README.md
- Consult the architecture documentation in ARCHITECTURE.md
- Check Thrad API integration docs in THREAD_API_INTEGRATION.md

---

**Good luck with your hackathon demo! 🚀**