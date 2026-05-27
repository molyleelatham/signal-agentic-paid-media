"""
Intelligence Service API.
"""
from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

from services.intelligence.tavily_client import MarketScanner, TavilyClient
from shared.utils.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Initialize Tavily client
    tavily_client = TavilyClient()
    app.state.tavily_client = tavily_client
    app.state.market_scanner = MarketScanner(tavily_client)
    
    yield
    
    # Cleanup
    await tavily_client.close()


app = FastAPI(
    title="Intelligence Service",
    description="Market intelligence ingestion for SIGNAL platform",
    version="0.1.0",
    lifespan=lifespan
)


# Request/Response Models
class MarketScanRequest(BaseModel):
    """Request model for market scan."""
    
    category: str = Field(..., description="Market category to scan")
    competitors: Optional[List[str]] = Field(default=None, description="List of competitor names")
    scan_depth: str = Field(default="advanced", description="Search depth (basic or advanced)")


class ConversationTheme(BaseModel):
    """Model for conversation theme."""
    
    theme: str
    example_post: str
    engagement_score: float


class CompetitorContent(BaseModel):
    """Model for competitor content."""
    
    competitor: str
    topic: str
    angle: str
    url: str


class IntelligenceDigest(BaseModel):
    """Model for intelligence digest."""
    
    audience_conversations: List[ConversationTheme]
    competitor_content: List[CompetitorContent]
    brand_mentions: List[dict]
    generated_at: Optional[str] = None


class MarketScanResponse(BaseModel):
    """Response model for market scan."""
    
    category: str
    market_intelligence: dict
    social_sentiment: List[dict]
    competitor_activity: List[dict]
    scan_timestamp: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Intelligence Service",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/intelligence/trigger-scan", response_model=MarketScanResponse)
async def trigger_scan(request: MarketScanRequest):
    """
    Trigger Tavily market scan.
    
    Performs comprehensive market scanning including:
    - Market intelligence via search_and_answer
    - Social sentiment analysis
    - Competitor activity monitoring
    """
    try:
        scanner = app.state.market_scanner
        
        scan_results = await scanner.scan_market(
            category=request.category,
            competitors=request.competitors,
            scan_depth=request.scan_depth
        )
        
        return MarketScanResponse(**scan_results)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.post("/intelligence/generate-digest", response_model=IntelligenceDigest)
async def generate_digest(scan_results: MarketScanResponse):
    """
    Generate weekly intelligence digest for marketers.
    
    Transforms raw scan results into a structured digest with:
    1. What your audience is talking about
    2. What competitors published
    3. Where you were mentioned
    """
    try:
        scanner = app.state.market_scanner
        
        digest = await scanner.generate_intelligence_digest(scan_results.dict())
        
        return IntelligenceDigest(**digest)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Digest generation failed: {str(e)}")


@app.get("/intelligence/tavily-status")
async def tavily_status():
    """Check Tavily API status."""
    try:
        client = app.state.tavily_client
        
        # Simple test query
        result = await client.search_and_answer(
            query="test query",
            max_results=1,
            days=1
        )
        
        return {
            "status": "operational",
            "api_key_configured": bool(client.api_key),
            "test_query_successful": True
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "api_key_configured": bool(app.state.tavily_client.api_key)
        }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "services.intelligence.api:app",
        host=settings.host,
        port=8001,  # Different port for intelligence service
        reload=settings.debug
    )