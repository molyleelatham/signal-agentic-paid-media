.PHONY: help install install-dev db-up db-down db-init db-reset db-migrate db-seed demo-data server test lint format clean overmind-setup

# Default target
help:
	@echo "SIGNAL Platform - Local Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make setup         - Complete setup (install + db-init + demo-data)"
	@echo ""
	@echo "Database (Docker):"
	@echo "  make db-up         - Start PostgreSQL and Redis with Docker"
	@echo "  make db-down       - Stop PostgreSQL and Redis"
	@echo "  make db-logs       - View database logs"
	@echo ""
	@echo "Database Operations:"
	@echo "  make db-init       - Initialize database schema"
	@echo "  make db-reset      - Reset database (drop and recreate)"
	@echo "  make db-migrate    - Run database migrations"
	@echo "  make db-seed       - Seed database with initial data"
	@echo ""
	@echo "Demo Data:"
	@echo "  make demo-data     - Populate Gymshark demo data"
	@echo ""
	@echo "Server:"
	@echo "  make server        - Start FastAPI server (localhost:8000)"
	@echo "  make server-reload - Start server with auto-reload"
	@echo "  make server-prod   - Start server in production mode"
	@echo ""
	@echo "Development:"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linters (ruff, mypy)"
	@echo "  make format        - Format code (black, ruff)"
	@echo "  make clean         - Clean up temporary files"
	@echo ""
	@echo "Overmind:"
	@echo "  make overmind-setup - Setup Overmind configuration"
	@echo ""
	@echo "Utilities:"
	@echo "  make check-deps    - Check if dependencies are installed"
	@echo "  make check-db      - Check database connection"
	@echo "  make check-env     - Check environment variables"

# Installation
install:
	@echo "Installing production dependencies..."
	pip install -e .

install-dev:
	@echo "Installing development dependencies..."
	pip install -e ".[dev]"

setup: install-dev db-init demo-data
	@echo "✅ Setup complete! Run 'make server' to start the server."

# Docker Database
db-up:
	@echo "Starting PostgreSQL and Redis with Docker..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo "Waiting for database to be ready..."
	@sleep 5
	@echo "✅ Database and Redis started"

db-down:
	@echo "Stopping PostgreSQL and Redis..."
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Database and Redis stopped"

db-logs:
	docker-compose -f docker-compose.dev.yml logs -f

# Database Operations
db-init:
	@echo "Initializing database schema..."
	python3 scripts/init_db.py
	@echo "✅ Database initialized"

db-reset:
	@echo "Resetting database..."
	@echo "⚠️  This will drop all tables and recreate schema"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		python3 scripts/reset_db.py; \
		echo "✅ Database reset"; \
	else \
		echo "❌ Cancelled"; \
	fi

db-migrate:
	@echo "Running database migrations..."
	alembic upgrade head
	@echo "✅ Migrations complete"

db-seed:
	@echo "Seeding database with initial data..."
	python3 scripts/seed_db.py
	@echo "✅ Database seeded"

# Demo Data
demo-data:
	@echo "Populating Gymshark demo data..."
	python3 scripts/demo_data.py
	@echo "✅ Gymshark demo data populated"

# Server
server:
	@echo "Starting FastAPI server on http://localhost:8000"
	uvicorn api.main:app --host 0.0.0.0 --port 8000

server-reload:
	@echo "Starting FastAPI server with auto-reload on http://localhost:8000"
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

server-prod:
	@echo "Starting server in production mode..."
	uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

# Development
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=.

lint:
	@echo "Running linters..."
	@echo "Running ruff..."
	ruff check .
	@echo "Running mypy..."
	mypy .
	@echo "✅ Linting complete"

format:
	@echo "Formatting code..."
	@echo "Running black..."
	black .
	@echo "Running ruff format..."
	ruff format .
	@echo "✅ Code formatted"

clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete"

# Utilities
check-deps:
	@echo "Checking dependencies..."
	@pip list | grep -E "(fastapi|uvicorn|sqlalchemy|asyncpg)" || echo "❌ Some dependencies missing"

check-db:
	@echo "Checking database connection..."
	python3 -c "import asyncio; from shared.database import engine; print('✅ Database connection OK')" || echo "❌ Database connection failed"

check-env:
	@echo "Checking environment variables..."
	@test -f .env && echo "✅ .env file exists" || echo "❌ .env file missing"
	@python3 -c "from shared.utils.settings import settings; print('✅ Settings loaded')" || echo "❌ Settings failed to load"

# Overmind Setup
overmind-setup:
	@echo "Setting up Overmind configuration..."
	python3 scripts/setup_overmind.py

# Quick start for local development
quickstart: db-up db-init demo-data server-reload