# Slack Message - Technical Summary

**SIGNAL Platform: AI-Powered Ad Optimization with LLM Evaluation Framework**

We built SIGNAL using **Overmind SDK** for agent orchestration with **LLMJudge** for 0-100 scoring of AI outputs. The framework includes:

• **5 AI Agents** (Bid Strategy, Content Brief, Creative Optimization, Market Analysis, Orchestration)
• **DisBERT Classification** - 13-segment model (A-M) with commercial intent scoring (10-95%)
• **Tavily Research** - Real-time web scraping with automatic field mapping
• **Tracing via Overmind** - Complete agent execution observability
• **Evaluation Framework** - 0-100 scoring on all AI outputs with performance metrics
• **Data Algorithms** - Bid Discovery Engine, Asymmetric PnL Calculator, Keyword Classification

**Tech Stack**: FastAPI, React, PostgreSQL, DisBERT BERT, Tavily API, Overmind SDK

**Key Innovation**: Automated pipeline from Tavily research → DisBERT classification → Agent execution → Commercial intent scoring → Bid optimization

Demo: http://localhost:5173 | API: http://localhost:8000/docs