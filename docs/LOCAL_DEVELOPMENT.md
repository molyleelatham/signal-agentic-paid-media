# Local Development Guide

## Quick Start

### 1. Start Database (Docker)
```bash
make db-up
```

This starts PostgreSQL and Redis with optimized settings for localhost.

### 2. Install Dependencies
```bash
make install-dev
```

### 3. Initialize Database
```bash
make db-init
```

### 4. Populate Demo Data
```bash
make demo-data
```

This populates the database with Gymshark demo data.

### 5. Start Server
```bash
make server-reload
```

The server will be available at http://localhost:8000

## One-Command Setup

```bash
make setup
```

This runs: install-dev → db-init → demo-data

## Available Commands

### Setup
```bash
make install       # Install production dependencies
make install-dev   # Install development dependencies
make setup         # Complete setup (install + db-init + demo-data)
```

### Database (Docker)
```bash
make db-up         # Start PostgreSQL and Redis
make db-down       # Stop PostgreSQL and Redis
make db-logs       # View database logs
```

### Database Operations
```bash
make db-init       # Initialize database schema
make db-reset      # Reset database (drop and recreate)
make db-migrate    # Run database migrations
make db-seed       # Seed database with initial data
```

### Demo Data
```bash
make demo-data     # Populate Gymshark demo data
```

### Overmind
```bash
make overmind-setup # Setup Overmind configuration
make register-agents # Register agents with Overmind
```

### Server
```bash
make server        # Start FastAPI server (no reload)
make server-reload # Start server with auto-reload (recommended for dev)
make server-prod   # Start server in production mode
```

### Development
```bash
make test          # Run tests
make lint          # Run linters (ruff, mypy)
make format        # Format code (black, ruff)
make clean         # Clean up temporary files
```

### Utilities
```bash
make check-deps    # Check if dependencies are installed
make check-db      # Check database connection
make check-env     # Check environment variables
```

## Environment Configuration

### Using .env.local

The project includes `.env.local` with optimized settings for localhost:

```bash
# Copy the local environment file
cp .env.local .env
```

### Database Connection

The `.env.local` file uses these localhost-optimized settings:
- **Database**: PostgreSQL on localhost:5432
- **User**: signal_user
- **Password**: signal_pass
- **Database**: signal
- **Pool Size**: 10 (lower for localhost)
- **Max Overflow**: 20
- **Pool Timeout**: 30s
- **Pool Recycle**: 3600s (1 hour)

### Redis Connection

- **URL**: redis://localhost:6379/0
- **Max Memory**: 512MB
- **Eviction Policy**: allkeys-lru

## Overmind Setup

Overmind is an AI tracing and evaluation platform. To set it up:

```bash
make overmind-setup
```

This will:
- Create `.overmind/` directory
- Create `.overmind/.env` configuration template
- Install Cursor IDE skills automatically

### Configure Overmind

Edit `.overmind/.env` and add your API keys:

```bash
# Get keys from: https://platform.overmind.ai/
OPENAI_API_KEY=sk-your-openai-key-here
OVERMIND_API_KEY=om-your-overmind-key-here
OVERMIND_PROJECT_ID=proj-your-project-id-here
```

### Get Overmind Credentials

1. Go to: https://platform.overmind.ai
2. Sign up or login
3. Create a new project
4. Copy API key and project ID
5. Add to `.overmind/.env`

### Overmind Integration

The SIGNAL platform uses Overmind for:
- Agent execution tracing
- LLM call monitoring
- Performance evaluation
- Token usage tracking
- Agent optimization

### Cursor Skills

Overmind automatically installs skills for Cursor IDE in `.cursor/skills/`:
- `overmind-generate-spec-and-dataset` - Generate specifications
- `overmind-optimize-agent` - Optimize agent performance
- `overmind-register-agent` - Register agents with Overmind

### Register Agents with Overmind

After configuring Overmind, register the SIGNAL platform agents:

```bash
make register-agents
```

This will output the Cursor IDE commands to register each agent:
- `bid_strategy_agent` - Makes strategic bidding decisions
- `content_brief_agent` - Generates creative briefs
- `creative_optimization_agent` - Optimizes creative performance
- `market_analysis_agent` - Analyzes market intelligence
- `orchestration_agent` - Coordinates all agents

**To register agents in Cursor IDE:**
1. Run `make register-agents` to see the commands
2. Copy each `/overmind-register-agent` command
3. Paste into Cursor IDE command palette
4. Run each `/overmind-optimize-agent` command after registration
5. Verify registration at https://platform.overmind.ai

**Agent Policies:**
Each agent has a policy file in `policies/` documenting:
- Agent purpose and capabilities
- Input/output schemas
- Decision criteria and constraints
- Integration points
- Optimization targets

See `policies/README.md` for detailed policy documentation.

## Database Optimization for Localhost

### PostgreSQL Settings (docker-compose.dev.yml)

The Docker Compose configuration includes these optimizations:
- **Max Connections**: 200
- **Shared Buffers**: 256MB
- **Effective Cache Size**: 1GB
- **Maintenance Work Mem**: 64MB
- **WAL Buffers**: 16MB
- **Random Page Cost**: 1.1 (SSD optimization)
- **Effective I/O Concurrency**: 200
- **Work Mem**: 1310kB
- **Min WAL Size**: 1GB
- **Max WAL Size**: 4GB

### Connection Pool Settings (shared/database/config.py)

- **Pool Size**: 10 (lower for localhost)
- **Max Overflow**: 20
- **Pool Timeout**: 30s
- **Pool Recycle**: 3600s (1 hour)
- **Pre-ping**: Enabled (verifies connections)
- **JIT**: Disabled (faster for small queries in dev)

## Testing the Terminal API

After starting the server, test the Bloomberg Terminal endpoints:

```bash
# Full dashboard data
curl http://localhost:8000/terminal/full-dashboard

# Header stats
curl http://localhost:8000/terminal/header-stats

# Channel metrics
curl http://localhost:8000/terminal/channel-metrics

# Campaign signals
curl http://localhost:8000/terminal/campaign-signals

# Strategy docs
curl http://localhost:8000/terminal/strategy-docs
```

## API Documentation

Once the server is running, access the interactive API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Database Connection Issues

```bash
# Check if database is running
make check-db

# View database logs
make db-logs

# Restart database
make db-down
make db-up
```

### Port Already in Use

If port 8000 is already in use, change it in `.env`:
```
APP_PORT=8001
```

### Permission Issues

If you get permission errors with Docker:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### Module Not Found Errors

If you get "ModuleNotFoundError", install dependencies:
```bash
make install-dev
```

## Development Workflow

### Typical Development Session

1. Start database: `make db-up`
2. Start server: `make server-reload`
3. Make changes to code
4. Server auto-reloads
5. Test changes
6. When done: `make db-down`

### Resetting Database

If you need to start fresh:
```bash
make db-reset    # Drops all tables
make demo-data   # Repopulates Gymshark data
```

## Performance Tips for Localhost

1. **Use server-reload**: Auto-reload is faster than manual restarts
2. **Keep pool size low**: 10 is sufficient for localhost (vs 20 for production)
3. **Disable JIT**: Faster for small queries in development
4. **Use pgAdmin** (optional): Access at http://localhost:5050
   - Email: admin@signal.local
   - Password: admin

## Additional Tools

### pgAdmin (Database GUI)

To enable pgAdmin:
```bash
docker-compose -f docker-compose.dev.yml --profile tools up -d
```

Access at: http://localhost:5050

### Redis CLI

To connect to Redis:
```bash
docker exec -it signal-redis-dev redis-cli
```

### PostgreSQL CLI

To connect to PostgreSQL:
```bash
docker exec -it signal-postgres-dev psql -U signal_user -d signal
```