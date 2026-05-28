🚀 Quick Start for Your Team

# 1. Setup environment
cp .env.example .env
# Edit with API keys

# 2. Install dependencies  
pip install -e ".[dev]"

# 3. Setup database
alembic upgrade head

# 4. Populate demo data
./scripts/setup_demo.sh

# 5. Start API server
uvicorn api.main:app --reload

# 6. Access API docs
http://localhost:8000/docs

# 7. Start Bloomberg-style React terminal (optional)
cd frontend && npm install && npm run dev
# http://localhost:5173 — Order Flow column + campaign SIGNAL tab

# SIGNAL - Autonomous Media Trading Platform

A sophisticated autonomous media trading platform that uses AI-driven intelligence to execute media buying decisions while keeping humans in the loop for creative and strategic decisions. Features an attention token economy that gamifies financial engineering in media buying.

## Architecture

SIGNAL is built as a modular microservices architecture:

- **Intelligence Service**: Ingests and processes multi-source market intelligence (Tavily, BERTopic, Thrad)
- **Trading Engine**: Executes bidding decisions using LOESS/DMR, Bayesian cold start, Thompson sampling
- **Token Service**: Manages the attention token economy with staking, leaderboards, and rewards
- **Platform Integration**: Executes bids on Meta, Google, and Thrad platforms
- **Analytics Service**: Calculates P&L, CAI risk, and integrates Overmind tracing

## Key Features

### AI-Driven Trading
- **LOESS/DMR Bid Discovery**: Non-parametric regression finds optimal bid points
- **Bayesian Cold Start**: James-Stein shrinkage for new campaigns
- **Thompson Sampling**: Dynamic budget allocation across platforms
- **Thrad Contextual Bidding**: Intent-based bid scaling
- **Adstock Decay Monitoring**: Tracks creative effectiveness over time

### Intelligence Layer
- **Tavily Search Agent**: Always-on market scanning
- **BERTopic Gap Matrix**: Topic clustering with zone classification
- **Thrad BERT Intent**: Demand context surface from LLM prompts
- **Competitive Intelligence**: Automated competitor monitoring

### Attention Token Economy
- **Proof-of-Conversion**: Tokens earned for efficient attention acquisition
- **Proof-of-Waste**: Tokens burned for wasted attention
- **Staking Mechanism**: Stake tokens on strategies for multiplier rewards
- **Leaderboard System**: Performance rankings with composite scoring
- **Achievement System**: Unlockable achievements for milestones

### Risk Management
- **Asymmetric P&L Scoring**: Loss-aversion principle applied to attention costs
- **CAI Risk Monitoring**: Goal-adjusted concentration risk assessment
- **Position Limits**: Risk-based position sizing
- **Supply Controls**: Automatic token supply management

## Project Structure

```
signal-platform/
├── services/
│   ├── intelligence/          # Intelligence ingestion service
│   ├── trading/               # Trading engine service
│   ├── token/                 # Token economy service
│   ├── platform_integration/  # Platform API integration
│   └── analytics/             # Analytics & optimization service
├── shared/
│   ├── models/                # Shared data models
│   ├── utils/                 # Shared utilities
│   └── database/              # Database configuration
├── tests/                     # Test suite
├── scripts/                   # Utility scripts
├── config/                    # Configuration files
├── ARCHITECTURE.md            # System architecture documentation
├── ATTENTION_TOKEN_DESIGN.md  # Token economy design
├── signal_technical_spec.md   # Technical specification
└── pyproject.toml             # Project dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker (for local development)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd adtech-hackathon
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -e ".[dev]"
```

4. Copy environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### LLM split: Cursor agents vs OpenAI (Overmind)

See [docs/LLM_ARCHITECTURE.md](docs/LLM_ARCHITECTURE.md) for the full picture.

| Layer | Provider | Keys |
|-------|----------|------|
| **SIGNAL agents** (runtime + Overmind eval harness) | Cursor SDK, **Composer 2.5** | `CURSOR_API_KEY`, `CURSOR_MODEL` |
| **Overmind** (setup, optimize, analyzer, datagen) | OpenAI via LiteLLM | `OPENAI_API_KEY`, `ANALYZER_MODEL` in `.overmind/.env` |
| **Overmind tracing** | Overmind platform | `OVERMIND_API_KEY` |

1. Add to `.env.local`:
```bash
CURSOR_API_KEY=cursor_...
CURSOR_MODEL=composer-2.5
OPENAI_API_KEY=sk-...          # required for overmind setup / optimize
OVERMIND_API_KEY=ovr_...
```
2. Sync into Overmind env:
```bash
python scripts/bootstrap_overmind_env.py
python scripts/test_cursor_sdk.py
```

**Cursor API** (`/api/v1/cursor/*`): direct Composer access from the app. **Overmind CLI** still uses OpenAI for its internal analyzer — that is expected.

5. Initialize database:
```bash
alembic upgrade head
```

6. Start Redis:
```bash
redis-server
```

7. Start Celery worker:
```bash
celery -A shared.database.celery_app worker --loglevel=info
```

8. Start API server:
```bash
uvicorn services.intelligence.api:app --reload
```

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
ruff check --fix .
mypy .
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

See `.env.example` for all required environment variables. Key variables include:

- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `TAVILY_API_KEY`: Tavily search API key
- `THRAD_API_KEY`: Thrad intent classification API key
- `OVERMIND_API_KEY`: Overmind tracing API key
- `JWT_SECRET_KEY`: Secret key for JWT authentication

## Stack Sponsors

- **Overmind**: LLM tracing and optimization
- **Tavily**: Market intelligence and search
- **Thrad AI**: BERT-based intent classification

## License

MIT License - see LICENSE file for details

## Contributing

This is a hackathon project. For production deployment considerations, please refer to the architecture documentation.