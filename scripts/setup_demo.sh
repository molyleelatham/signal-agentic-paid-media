#!/bin/bash

# Demo setup script for Acme fashion e-commerce client
# This script populates the database with demo data for the hackathon demonstration

set -e

echo "🎨 Setting up Acme Fashion demo data..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it with required environment variables."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Run the demo data script
echo "🗄️  Populating database with demo data..."
python scripts/demo_data.py

echo ""
echo "✅ Demo setup complete!"
echo ""
echo "📊 Demo data summary:"
echo "   - Client: Acme Fashion"
echo "   - Campaigns: 4 active campaigns across Meta, Google, TikTok, Microsoft"
echo "   - Content Briefs: 3 briefs based on Tavily intelligence"
echo "   - Topic Clusters: 3 clusters with SEO and geo optimization data"
echo "   - Creatives: 4 creatives with platform placements"
echo "   - Efficiency Metrics: 60 days of performance data showing improvements"
echo "   - Budget Allocations: 4 weeks of allocation history"
echo "   - Token Transactions: 6 transactions showing rewards and penalties"
echo ""
echo "🚀 Start the API server:"
echo "   uvicorn api.main:app --reload"
echo ""
echo "📡 Demo API endpoints:"
echo "   GET  /api/v1/demo/dashboard/overview?client_id=<client_id>"
echo "   GET  /api/v1/demo/dashboard/briefs?client_id=<client_id>"
echo "   GET  /api/v1/demo/dashboard/allocations?client_id=<client_id>"
echo "   GET  /api/v1/demo/intelligence/tavily-results?client_id=<client_id>"
echo "   GET  /api/v1/demo/intelligence/topic-clusters?client_id=<client_id>"
echo "   GET  /api/v1/demo/planning/cpl-matrix?client_id=<client_id>&target_leads=1000"
echo "   POST /api/v1/demo/planning/scenario-builder?client_id=<client_id>"
echo "   POST /api/v1/demo/agents/chat?client_id=<client_id>&message=<message>"
echo "   GET  /api/v1/demo/agents/efficiency-metrics?client_id=<client_id>"
echo "   GET  /api/v1/demo/creatives?client_id=<client_id>"
echo "   POST /api/v1/demo/creatives/upload?client_id=<client_id>"
echo "   POST /api/v1/demo/creatives/bulk-upload?client_id=<client_id>"
echo "   GET  /api/v1/demo/intelligence/keywords?client_id=<client_id>&topic=<topic>&platform=<platform>"
echo "   GET  /api/v1/demo/campaigns/performance?client_id=<client_id>"
echo "   GET  /api/v1/demo/campaigns/business-kpis?client_id=<client_id>"
echo ""
echo "📖 For full API documentation, visit: http://localhost:8000/docs"