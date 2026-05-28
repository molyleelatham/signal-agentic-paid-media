# Hackathon Overview: Technology Integration

---

## Overmind Integration

We integrated **Overmind SDK** to orchestrate and manage our AI agents. Overmind provides a unified platform for agent registration, execution, and monitoring. We registered 5 core AI agents (Bid Strategy, Content Brief, Creative Optimization, Market Analysis, and Orchestration) with Overmind, enabling centralized agent management, observability, and scalable execution. The SDK handles agent lifecycle, performance tracking, and provides a unified interface for triggering agents across different services in our platform.

---

## Tavily Research Integration

**Tavily API** powers our web research capabilities for discovering trending topics and market insights. When users enter a research query, Tavily performs comprehensive web scraping across multiple sources including Reddit discussions, SEO pages, and Google search results. We implemented an intelligent mapper that automatically categorizes Tavily research results into DisBERT's 13 classification segments (A-M), enabling us to identify high-value content (purchasable products, personal reflections, guidance topics) with commercial intent scoring. This integration allows our platform to surface real-time trending topics and automatically classify them for ad targeting and content strategy.

---

## Algorithm Implementation

We implemented several key algorithms to power our ad optimization platform. The **Bid Discovery Engine** uses algorithmic components to calculate optimal bid amounts based on market conditions, competition, and historical performance. Our **Asymmetric PnL Calculator** tracks attention token trading with risk-adjusted returns, enabling sophisticated trading strategies. The **DisBERT Classification Algorithm** automatically classifies content into 13 segments (A-M) based on keywords, intent, and content type, with commercial intent scoring ranging from 0.10 to 0.95. Additionally, we implemented a **Keyword Classification System** using DisBERT BERT models to categorize keywords for Google Ads targeting, and a **Content Optimization Algorithm** that analyzes performance data to recommend creative improvements.

---

## AI Agent Orchestration

Our **Agent Trigger Service** provides a unified interface for triggering 6 different agent types: bid optimization, content generation, creative optimization, market analysis, keyword classification, and full orchestration. Each agent operates independently but can be coordinated through the Orchestration Agent. The system tracks execution metrics including tokens used, execution time, and cost, providing transparency into agent performance. Agents are reactive - they can be triggered manually via UI buttons or programmatically through API endpoints, with real-time feedback displayed in our terminal-inspired frontend.

---

## Data Pipeline Architecture

We built a sophisticated data pipeline that flows from research to activation. Tavily research feeds into our DisBERT mapper, which segments content by classification and commercial intent. These segments are then used to generate trending topics for our Market Intelligence dashboard, where users can view high-value opportunities. The pipeline also supports keyword extraction, content idea generation, and Thrad BERT input creation, creating a comprehensive intelligence layer that powers our ad optimization and trading decisions. All data is logged to our agent execution logger for audit trails and performance analysis.

---

## Frontend Reactive Architecture

Our React frontend is built with **TanStack Query** for reactive state management, enabling real-time updates when agents execute. We implemented custom SVG charting components for visualizing volume trends, growth rates, and performance metrics. The terminal-inspired dark theme provides a professional interface for monitoring agent signals and market intelligence. Key features include agent trigger buttons with loading states, success/failure visual feedback, execution time display, and a DisBERT segments panel that automatically appears after Tavily research, showing classification results with color-coded priority indicators.

---

## Key Achievements

- **6 AI Agents** registered and orchestrated via Overmind
- **13 DisBERT Classifications** with automatic field mapping
- **Real-time Trending Topics** powered by Tavily research
- **Reactive UI** with agent trigger buttons and live feedback
- **Commercial Intent Scoring** for identifying high-value segments
- **Attention Token Trading** with asymmetric PnL calculation
- **Keyword Classification** for Google Ads targeting
- **Comprehensive Logging** for agent execution tracking

---

## Technology Stack Summary

- **Agent Orchestration**: Overmind SDK
- **Web Research**: Tavily API
- **Content Classification**: DisBERT BERT Models
- **Backend**: FastAPI (Python)
- **Frontend**: React + TypeScript + TanStack Query
- **Database**: PostgreSQL with SQLAlchemy
- **Trading**: Custom bid discovery and PnL algorithms
- **Visualization**: Custom SVG charts

---

This integration enables our SIGNAL platform to deliver AI-powered ad optimization with real-time market intelligence, automated content classification, and intelligent trading strategies.