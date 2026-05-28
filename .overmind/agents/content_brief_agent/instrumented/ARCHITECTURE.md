# SIGNAL - Backend Architecture Design

## Overview

SIGNAL is an autonomous media trading platform that uses AI-driven intelligence to execute media buying decisions while keeping humans in the loop for creative and strategic decisions. The backend is designed as a modular microservices architecture with strong separation of concerns.

## Core Philosophy

- **Human-in-the-loop autonomous**: AI executes trading decisions, humans make creative/strategic choices
- **Intelligence-first**: All trading decisions are driven by multi-source intelligence (Tavily, Thrad BERT)
- **Financial engineering gamification**: Attention tokens create a game-theoretic framework for media buying
- **Technical excellence**: Open-source models, auditable decisions, Overmind tracing for optimization

## Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (FastAPI)                     │
│                  Rate limiting, Auth, Routing                    │
└───────────────────────────┬─────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Intelligence │   │   Trading     │   │    Token      │
│   Service     │   │   Engine      │   │   Service     │
└───────┬───────┘   └───────┬───────┘   └───────┬───────┘
        │                   │                   │
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Tavily       │   │  Bid          │   │  Attention    │
│  Ingestor     │   │  Discovery    │   │  Token Bank   │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  BERTopic     │   │  Budget       │   │  Token        │
│  Gap Matrix   │   │  Allocator    │   │  Marketplace  │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│  Thrad        │   │  Adstock      │   │  Leaderboard  │
│  Intent       │   │  Monitor      │   │  System       │
└───────────────┘   └───────────────┘   └───────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │  P&L Scorer   │
                    │  + CAI Risk   │
                    └───────────────┘
```

## Service Boundaries

### 1. Intelligence Service
**Responsibility**: Ingest and process multi-source market intelligence

**Components**:
- Tavily Search Agent (always-on market scanner)
- BERTopic Gap Matrix (topic clustering + zone classification)
- Thrad Intent Signal Integration (demand context surface)
- Competitive Intelligence (crawler + summarizer)

**Data Flow**:
```
Tavily API → Document Corpus → BERTopic → Topic Clusters + Zone Labels
                                                  ↓
                                          Thrad Intent Volume
                                                  ↓
                                    Gap Matrix (Competitor vs Intent vs Brand)
```

**API Endpoints**:
- `POST /intelligence/trigger-scan` - Trigger Tavily scan
- `GET /intelligence/gap-matrix` - Get current gap matrix
- `GET /intelligence/topic-clusters` - Get topic clusters with zones
- `GET /intelligence/intent-map/{topic}` - Get Thrad intent volume for topic

### 2. Trading Engine Service
**Responsibility**: Execute bidding decisions and portfolio management

**Components**:
- LOESS/DMR Bid Discovery (price discovery)
- Bayesian Cold Start (James-Stein shrinkage)
- Thompson Sampling Budget Allocator (cross-platform allocation)
- Thrad Contextual Bid (intent-based bid scaling)
- Adstock Decay Monitor (creative effectiveness tracking)
- CAI Risk Monitor (concentration risk management)

**Data Flow**:
```
Auction Event → Bid Discovery → Intent Scaling → Decay Check → Budget Check → Final Bid
                      ↓              ↓              ↓              ↓
              LOESS/DMR      Thrad Context   Adstock      Thompson Allocation
              + Bayesian     Scaling         Signal       (platform budget)
```

**API Endpoints**:
- `POST /trading/compute-bid` - Compute bid for auction event
- `GET /trading/bid-curve/{cluster}` - Get LOESS bid curve
- `GET /trading/budget-allocation` - Get current platform allocation
- `GET /trading/decay-status/{position}` - Get adstock decay status
- `GET /trading/cai-risk/{campaign}` - Get concentration risk assessment

### 3. Token Service
**Responsibility**: Attention token economy and gamification

**Components**:
- Attention Token Bank (token issuance, burning, transfers)
- Token Marketplace (optional trading between users)
- Leaderboard System (performance rankings)
- Token Rewards Engine (P&L → token conversion)
- Staking Mechanism (stake tokens on campaign strategies)

**Attention Token Economics**:
- Tokens represent "units of attention" successfully converted
- Earned through positive P&L (efficient attention acquisition)
- Lost through negative P&L (wasted attention)
- Can be staked on campaign strategies for multiplier rewards
- Leaderboard rankings based on token balance + risk-adjusted returns

**API Endpoints**:
- `GET /token/balance/{user}` - Get token balance
- `POST /token/stake` - Stake tokens on strategy
- `GET /token/leaderboard` - Get performance leaderboard
- `POST /token/transfer` - Transfer tokens (if marketplace enabled)
- `GET /token/rewards/{campaign}` - Get token rewards for campaign

### 4. Platform Integration Service
**Responsibility**: Execute bids on external platforms

**Components**:
- Meta Marketing API Integration
- Google Ads API Integration
- Thrad DSP API Integration
- Bid Execution Engine
- Performance Data Ingestion

**API Endpoints**:
- `POST /platform/execute-bid` - Execute bid on platform
- `GET /platform/performance/{campaign}` - Get performance data
- `POST /platform/sync-performance` - Trigger performance sync

### 5. Analytics & Optimization Service
**Responsibility**: P&L calculation, Overmind integration, optimization

**Components**:
- Asymmetric P&L Scorer (with attention token rewards)
- CAI Risk Calculator
- Overmind Agent Tracing
- Creative Scoring (CLIP, sentence transformers)
- Performance Analytics

**API Endpoints**:
- `GET /analytics/pnl/{position}` - Get P&L score
- `GET /analytics/cai-risk/{campaign}` - Get concentration risk
- `POST /analytics/overmind-trace` - Submit Overmind trace
- `GET /analytics/creative-score/{creative}` - Get creative quality score

## Attention Token System Design

### Token Model

Attention Tokens (ATTN) are the native cryptocurrency of the SIGNAL platform, representing successful attention acquisition and conversion.

**Token Properties**:
- Total supply: Dynamic (expands/contracts based on platform performance)
- Token type: Utility token (not security)
- Issuance: Proof-of-Conversion (minted when attention converts efficiently)
- Burning: Proof-of-Waste (burned when attention is wasted)

### Token Economics

#### Earning Tokens

Tokens are earned through efficient attention acquisition:

```python
def calculate_token_reward(pnl_score: dict, difficulty_multiplier: float = 1.0) -> float:
    """
    Calculate token reward based on P&L efficiency.
    
    pnl_score: {
        "gross_revenue": float,
        "attention_waste_cost": float,
        "net_pnl": float,
        "efficiency_ratio": float
    }
    """
    # Base reward: net P&L converted to tokens
    base_reward = max(0, pnl_score["net_pnl"]) * 0.1  # 1 token = $10 revenue
    
    # Efficiency bonus: higher efficiency ratio = bonus tokens
    efficiency_bonus = max(0, pnl_score["efficiency_ratio"] - 1.0) * 5
    
    # Difficulty multiplier: harder markets = more tokens
    final_reward = (base_reward + efficiency_bonus) * difficulty_multiplier
    
    return final_reward
```

#### Losing Tokens

Tokens are burned when attention is wasted:

```python
def calculate_token_penalty(pnl_score: dict, stake_amount: float = 0.0) -> float:
    """
    Calculate token penalty for wasted attention.
    
    If user has staked tokens, penalty is deducted from stake first.
    """
    if pnl_score["net_pnl"] >= 0:
        return 0.0
    
    # Penalty: 50% of losses converted to token burn
    penalty = abs(pnl_score["net_pnl"]) * 0.05  # 1 token = $10 loss
    
    # If staked, burn from stake (with multiplier)
    if stake_amount > 0:
        stake_burn = min(stake_amount, penalty * 1.5)  # 1.5x multiplier on stakes
        return stake_burn
    
    return penalty
```

#### Staking Mechanism

Users can stake tokens on specific campaign strategies:

```python
@dataclass
class TokenStake:
    user_id: str
    campaign_id: str
    strategy_id: str
    stake_amount: float
    staked_at: datetime
    multiplier: float = 1.0  # Based on stake size and duration
    status: str = "active"

def calculate_stake_multiplier(stake_amount: float, duration_days: int) -> float:
    """
    Calculate reward multiplier based on stake size and duration.
    
    - Larger stakes = higher multiplier (up to 2.0x)
    - Longer duration = higher multiplier (up to 1.5x)
    """
    size_multiplier = min(2.0, 1.0 + (stake_amount / 1000.0))  # 1000 tokens = 2.0x
    duration_multiplier = min(1.5, 1.0 + (duration_days / 30.0))  # 30 days = 1.5x
    
    return size_multiplier * duration_multiplier
```

#### Leaderboard System

```python
@dataclass
class LeaderboardEntry:
    user_id: str
    token_balance: float
    risk_adjusted_return: float  # Sharpe ratio equivalent
    total_conversions: int
    efficiency_score: float
    rank: int

def calculate_risk_adjusted_return(pnl_history: list[float]) -> float:
    """
    Calculate Sharpe-like ratio for risk-adjusted performance.
    """
    if len(pnl_history) < 2:
        return 0.0
    
    returns = np.array(pnl_history)
    mean_return = returns.mean()
    std_return = returns.std()
    
    if std_return == 0:
        return mean_return
    
    return mean_return / std_return
```

### Token Flow Diagram

```
┌─────────────┐
│  Campaign   │
│  Execution  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  P&L Scorer │
│  (Module 8) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  Token Rewards Engine       │
│  - Calculate reward/penalty │
│  - Apply stake multipliers  │
│  - Mint/burn tokens         │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Token Bank                 │
│  - Update balances          │
│  - Process stakes           │
│  - Record transactions      │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  Leaderboard System         │
│  - Update rankings          │
│  - Calculate risk scores    │
└─────────────────────────────┘
```

## Technology Stack

### Core Framework
- **FastAPI**: High-performance async API framework
- **Pydantic**: Data validation and settings management
- **SQLAlchemy**: ORM for database operations
- **Alembic**: Database migrations

### Task Processing
- **Celery**: Distributed task queue
- **Redis**: Message broker and caching
- **Flower**: Celery monitoring

### Database
- **PostgreSQL**: Primary database (via Supabase)
- **Redis**: Caching and session management

### Machine Learning
- **BERTopic**: Topic modeling
- **sentence-transformers**: Text embeddings
- **scikit-learn**: Similarity calculations
- **statsmodels**: LOESS regression
- **scipy**: Optimization and spline fitting
- **torch + CLIP**: Visual scoring

### Integrations
- **Tavily**: Market intelligence API
- **Thrad**: Intent classification API
- **Overmind**: LLM tracing and optimization
- **Modal**: Serverless GPU inference

### Monitoring & Observability
- **Overmind**: Agent tracing and optimization
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **Sentry**: Error tracking

## Database Schema

### Core Tables

```sql
-- Users and authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    token_balance DECIMAL(18, 8) DEFAULT 0.0
);

-- Campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    goal_type VARCHAR(50) NOT NULL, -- lead_generation, customer_acquisition, etc.
    total_budget DECIMAL(18, 2) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Topic clusters from BERTopic
CREATE TABLE topic_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    name VARCHAR(255) NOT NULL,
    zone VARCHAR(50) NOT NULL, -- gap, contested, owned, ignore, monitor
    competitor_score DECIMAL(5, 4),
    intent_score DECIMAL(5, 4),
    brand_score DECIMAL(5, 4),
    velocity DECIMAL(10, 4), -- topic velocity
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Media positions (ads)
CREATE TABLE media_positions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    topic_cluster_id UUID REFERENCES topic_clusters(id),
    platform VARCHAR(50) NOT NULL, -- meta, google, thrad
    creative_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Bid decisions
CREATE TABLE bid_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID REFERENCES media_positions(id),
    platform VARCHAR(50) NOT NULL,
    bid_amount DECIMAL(10, 2) NOT NULL,
    intent_context JSONB, -- Thrad intent scores
    loess_optimal DECIMAL(10, 2),
    posterior_confidence DECIMAL(5, 4),
    decay_signal VARCHAR(50),
    action VARCHAR(50) NOT NULL, -- bid, pause, skip
    reason VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance data
CREATE TABLE performance_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID REFERENCES media_positions(id),
    date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    spend DECIMAL(18, 2) DEFAULT 0.0,
    revenue DECIMAL(18, 2) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- P&L scores
CREATE TABLE pnl_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID REFERENCES media_positions(id),
    date DATE NOT NULL,
    gross_revenue DECIMAL(18, 2) NOT NULL,
    attention_waste_cost DECIMAL(18, 2) NOT NULL,
    net_pnl DECIMAL(18, 2) NOT NULL,
    efficiency_ratio DECIMAL(10, 4),
    lambda_applied DECIMAL(5, 2) DEFAULT 2.0,
    token_reward DECIMAL(18, 8) DEFAULT 0.0,
    token_penalty DECIMAL(18, 8) DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Token transactions
CREATE TABLE token_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    position_id UUID REFERENCES media_positions(id),
    transaction_type VARCHAR(50) NOT NULL, -- reward, penalty, stake, unstake, transfer
    amount DECIMAL(18, 8) NOT NULL,
    balance_after DECIMAL(18, 8) NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Token stakes
CREATE TABLE token_stakes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    campaign_id UUID REFERENCES campaigns(id),
    strategy_id VARCHAR(255),
    stake_amount DECIMAL(18, 8) NOT NULL,
    multiplier DECIMAL(5, 4) DEFAULT 1.0,
    status VARCHAR(50) DEFAULT 'active', -- active, completed, liquidated
    staked_at TIMESTAMP DEFAULT NOW(),
    unstaked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Budget allocation (Thompson sampling)
CREATE TABLE budget_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    platform VARCHAR(50) NOT NULL,
    allocated_budget DECIMAL(18, 2) NOT NULL,
    alpha DECIMAL(10, 4) DEFAULT 2.0, -- Beta distribution parameter
    beta DECIMAL(10, 4) DEFAULT 2.0, -- Beta distribution parameter
    week INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Overmind traces
CREATE TABLE overmind_traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trace_id VARCHAR(255) UNIQUE NOT NULL,
    function_name VARCHAR(255) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    latency_ms INTEGER,
    cost_usd DECIMAL(10, 6),
    quality_score DECIMAL(5, 4),
    outcome_label VARCHAR(50),
    outcome_value DECIMAL(18, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Intelligence documents (Tavily)
CREATE TABLE intelligence_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id),
    source_type VARCHAR(50) NOT NULL, -- competitor, market, social, brand
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(768), -- sentence-transformers embedding
    created_at TIMESTAMP DEFAULT NOW()
);

-- Adstock decay data
CREATE TABLE adstock_decay (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    position_id UUID REFERENCES media_positions(id),
    lambda_decay DECIMAL(5, 4),
    std_error DECIMAL(5, 4),
    signal VARCHAR(50) NOT NULL, -- hold, reduce, exit
    confidence VARCHAR(50),
    calculated_at TIMESTAMP DEFAULT NOW()
);
```

## Data Flow Architecture

### Real-time Bidding Flow

```
1. Platform Integration Service receives auction event
   ↓
2. Trading Engine computes bid:
   - LOESS/DMR bid discovery
   - Bayesian shrinkage if cold start
   - Thrad contextual scaling
   - Adstock decay check
   - Budget allocation check
   ↓
3. Bid executed via Platform Integration Service
   ↓
4. Performance data ingested (async)
   ↓
5. P&L calculated → Token rewards/penalties
   ↓
6. Overmind trace logged with outcome
   ↓
7. Models updated (weekly re-fit)
```

### Batch Intelligence Flow

```
1. Tavily scan triggered (daily/weekly)
   ↓
2. Documents ingested → Embeddings computed
   ↓
3. BERTopic clustering → Topic clusters + zones
   ↓
4. Thrad intent volume fetched per topic
   ↓
5. Gap matrix updated
   ↓
6. Marketer notified of new intelligence
   ↓
7. Trading engine uses updated signals
```

## Deployment Architecture

### Development Environment
- Local Docker Compose setup
- PostgreSQL, Redis, Celery worker
- FastAPI with auto-reload

### Production Environment
- Kubernetes deployment
- Horizontal pod autoscaling
- Managed PostgreSQL (Supabase)
- Redis Cluster
- Celery with RabbitMQ
- CDN for static assets

### GPU Inference
- Modal for serverless GPU
- CLIP model inference
- BERTopic inference on-demand

## Security Considerations

- API key rotation for external services (Tavily, Thrad, Overmind)
- Rate limiting per user
- Input validation on all endpoints
- SQL injection prevention (parameterized queries)
- Token transfer validation (if marketplace enabled)
- Audit logging for all token transactions

## Monitoring & Alerting

- Overmind trace quality monitoring
- Token economy health metrics
- P&L performance dashboards
- Bid latency monitoring
- Error rate alerting
- Budget exhaustion alerts

## Next Steps

1. Set up project structure with all services
2. Implement database schema with Alembic migrations
3. Build Intelligence Service with Tavily integration
4. Build Trading Engine with bid discovery
5. Implement Token Service with attention economics
6. Integrate Overmind tracing across all services
7. Set up Celery for async task processing
8. Deploy and test end-to-end flow