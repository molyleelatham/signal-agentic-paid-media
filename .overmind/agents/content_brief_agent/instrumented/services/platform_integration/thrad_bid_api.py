"""
Thrad Bid API Client for Ad Auction Orchestration.

This integrates with Thrad's paid LLM API for multi-bidder auctions,
replacing local bid discovery with Thrad's auction orchestration.
"""
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from pydantic import BaseModel, Field

from shared.utils.settings import settings


class ThradBidRequest(BaseModel):
    """Request model for Thrad Bid API."""
    
    # Required fields
    userId: str = Field(..., description="Unique anonymous user identifier")
    
    # Contextual fields (required for contextual ads)
    chatId: Optional[str] = Field(None, description="Conversation identifier")
    messages: Optional[List[Dict]] = Field(None, description="Conversation history")
    
    # Configuration
    config: Optional[Dict] = Field(None, description="Publisher configuration")
    request_type: str = Field(default="contextual", description="Pipeline selector")
    ad_formats: Optional[List[str]] = Field(None, description="Ad formats to render")
    
    # Optional fields
    turn_number: Optional[int] = Field(None, description="Current turn in conversation")
    turns_from_last_ad: Optional[int] = Field(None, description="Turns since last ad")
    summary: Optional[str] = Field(None, description="Conversation summary")
    force: bool = Field(default=False, description="Force ad as last resort")
    
    # User metadata
    user_metadata: Optional[Dict] = Field(None, description="User targeting metadata")


class ThradBidResponse(BaseModel):
    """Response model from Thrad Bid API."""
    
    requestId: str
    timestamp: str
    totalTime: float
    status: str
    message: str
    data: Dict
    error: Optional[Dict] = None


class ThradBidAPIClient:
    """
    Client for Thrad Bid API integration.
    
    This client handles:
    - Multi-bidder auction orchestration
    - Contextual and opener ad formats
    - Sponsored messages and polls
    - Real-time bidding and creative selection
    """
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.thrads.ai"):
        """
        Initialize Thrad Bid API client.
        
        Args:
            api_key: Thrad API key. If not provided, uses settings.
            base_url: Thrad API base URL
        """
        self.api_key = api_key or settings.thrad_api_key
        if not self.api_key:
            raise ValueError("Thrad API key is required for Bid API integration")
        
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
    
    async def request_bid(
        self,
        user_id: str,
        request_type: str = "contextual",
        chat_id: Optional[str] = None,
        messages: Optional[List[Dict]] = None,
        config: Optional[Dict] = None,
        ad_formats: Optional[List[str]] = None,
        user_metadata: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> ThradBidResponse:
        """
        Request a bid from Thrad's multi-bidder auction.
        
        Args:
            user_id: Unique anonymous user identifier
            request_type: "contextual" or "opener"
            chat_id: Conversation identifier (required for contextual)
            messages: Conversation history (required for contextual)
            config: Publisher configuration
            ad_formats: Ad formats to render
            user_metadata: User targeting metadata
            headers: Additional headers (X-Forwarded-For, User-Agent, etc.)
        
        Returns:
            ThradBidResponse with winning bid or null if no bids
        """
        # Build request body
        request_body = {
            "userId": user_id,
            "request_type": request_type
        }
        
        # Add contextual fields
        if request_type == "contextual":
            if not chat_id:
                raise ValueError("chatId is required for contextual requests")
            if not messages:
                raise ValueError("messages is required for contextual requests")
            
            request_body["chatId"] = chat_id
            request_body["messages"] = messages
        
        # Add optional fields
        if config:
            request_body["config"] = config
        if ad_formats:
            request_body["ad_formats"] = ad_formats
        if user_metadata:
            request_body["user_metadata"] = user_metadata
        
        # Build headers
        request_headers = {
            "thrad-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Add user identification headers
        if headers:
            request_headers.update(headers)
        
        # Make API request
        response = await self.client.post(
            f"{self.base_url}/api/v1/bid",
            json=request_body,
            headers=request_headers
        )
        
        response.raise_for_status()
        
        # Parse response
        data = response.json()
        
        return ThradBidResponse(**data)
    
    async def request_contextual_ad(
        self,
        user_id: str,
        chat_id: str,
        messages: List[Dict],
        ad_formats: List[str] = None,
        config: Dict = None
    ) -> ThradBidResponse:
        """
        Request a contextual ad (in-chat).
        
        Args:
            user_id: User identifier
            chat_id: Conversation identifier
            messages: Conversation history
            ad_formats: Ad formats (sponsored_message, sponsored_poll, or both)
            config: Publisher configuration
        
        Returns:
            ThradBidResponse with contextual ad
        """
        return await self.request_bid(
            user_id=user_id,
            request_type="contextual",
            chat_id=chat_id,
            messages=messages,
            ad_formats=ad_formats or ["sponsored_message"],
            config=config
        )
    
    async def request_opener_ad(
        self,
        user_id: str,
        ad_formats: List[str] = None,
        config: Dict = None
    ) -> ThradBidResponse:
        """
        Request an opener ad (pre-chat).
        
        Args:
            user_id: User identifier
            ad_formats: Ad formats (sponsored_message, sponsored_prompt, or both)
            config: Publisher configuration
        
        Returns:
            ThradBidResponse with opener ad
        """
        return await self.request_bid(
            user_id=user_id,
            request_type="opener",
            ad_formats=ad_formats or ["sponsored_prompt"],
            config=config
        )
    
    def build_message_history(
        self,
        conversation_text: str,
        user_message: str = None,
        assistant_response: str = None
    ) -> List[Dict]:
        """
        Build message history for Thrad API.
        
        Args:
            conversation_text: Full conversation text
            user_message: Latest user message (optional)
            assistant_response: Latest assistant response (optional)
        
        Returns:
            Formatted message history array
        """
        messages = []
        timestamp = datetime.utcnow().isoformat()
        
        # Add conversation as user message
        if conversation_text:
            messages.append({
                "role": "user",
                "content": conversation_text,
                "timestamp": timestamp
            })
        
        # Add latest user message if provided
        if user_message:
            messages.append({
                "role": "user",
                "content": user_message,
                "timestamp": timestamp
            })
        
        # Add assistant response if provided
        if assistant_response:
            messages.append({
                "role": "assistant",
                "content": assistant_response,
                "timestamp": timestamp
            })
        
        return messages
    
    def extract_bid_info(self, response: ThradBidResponse) -> Dict:
        """
        Extract relevant bid information from Thrad response.
        
        Args:
            response: ThradBidResponse
        
        Returns:
            Dictionary with bid information
        """
        if response.data.get("bid") is None:
            return {
                "won_bid": False,
                "price": 0.0,
                "ad_format": None,
                "advertiser": None
            }
        
        bid = response.data["bid"]
        
        return {
            "won_bid": True,
            "price": bid.get("price", 0.0),
            "ad_format": bid.get("ad_format"),
            "advertiser": bid.get("advertiser"),
            "domain": bid.get("domain"),
            "headline": bid.get("headline"),
            "description": bid.get("description"),
            "cta_text": bid.get("cta_text"),
            "url": bid.get("url"),
            "placement": bid.get("placement"),
            "logo_url": bid.get("logo_url"),
            "image_url": bid.get("image_url"),
            "view_url": bid.get("view_url"),
            "dsp": bid.get("dsp"),
            "bid_id": bid.get("bidId"),
            # Poll-specific fields
            "sponsored_poll_id": bid.get("sponsored_poll_id"),
            "question": bid.get("question"),
            "options": bid.get("options"),
            "vote_url": bid.get("vote_url"),
            "results_url": bid.get("results_url"),
            "cta_url": bid.get("cta_url"),
            "results": bid.get("results")
        }


class ThradAuctionIntegrator:
    """
    Integration layer for Thrad's auction system.
    
    This replaces the local bid discovery with Thrad's multi-bidder auction,
    while keeping the agent system for strategic decisions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Thrad auction integrator.
        
        Args:
            api_key: Thrad API key
        """
        self.thrad_client = ThradBidAPIClient(api_key)
    
    async def orchestrate_auction(
        self,
        user_id: str,
        conversation_context: Dict,
        agent_recommendations: Dict = None
    ) -> Dict:
        """
        Orchestrate auction using Thrad's bid API with agent enhancements.
        
        Args:
            user_id: User identifier
            conversation_context: Conversation context and messages
            agent_recommendations: Optional agent strategic recommendations
        
        Returns:
            Auction result with Thrad bid and agent insights
        """
        # Build message history from conversation context
        messages = self._build_messages_from_context(conversation_context)
        
        # Apply agent recommendations to config
        config = self._apply_agent_config(agent_recommendations)
        
        # Request bid from Thrad
        thrad_response = await self.thrad_client.request_contextual_ad(
            user_id=user_id,
            chat_id=conversation_context.get("chat_id"),
            messages=messages,
            config=config
        )
        
        # Extract bid information
        bid_info = self.thrad_client.extract_bid_info(thrad_response)
        
        # Combine with agent insights
        result = {
            "thrad_response": {
                "request_id": thrad_response.requestId,
                "timestamp": thrad_response.timestamp,
                "total_time": thrad_response.totalTime,
                "status": thrad_response.status,
                "message": thrad_response.message
            },
            "bid": bid_info,
            "agent_insights": agent_recommendations or {},
            "auction_source": "thrad_multi_bidder"
        }
        
        return result
    
    def _build_messages_from_context(self, context: Dict) -> List[Dict]:
        """
        Build message history from conversation context.
        
        Args:
            context: Conversation context dictionary
        
        Returns:
            Formatted message history
        """
        messages = []
        
        # Handle different context formats
        if "messages" in context:
            # Already in correct format
            messages = context["messages"]
        elif "conversation_text" in context:
            # Build from text
            messages = self.thrad_client.build_message_history(
                conversation_text=context["conversation_text"],
                user_message=context.get("user_message"),
                assistant_response=context.get("assistant_response")
            )
        else:
            # Build minimal message from available context
            messages.append({
                "role": "user",
                "content": context.get("query", "User query"),
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return messages
    
    def _apply_agent_config(self, agent_recommendations: Dict) -> Dict:
        """
        Apply agent recommendations to Thrad config.
        
        Args:
            agent_recommendations: Agent strategic recommendations
        
        Returns:
            Thrad config with agent enhancements
        """
        config = {}
        
        if not agent_recommendations:
            return config
        
        # Map agent recommendations to Thrad config
        if agent_recommendations.get("ad_frequency_control"):
            config["max_frequency"] = agent_recommendations["ad_frequency_control"]
        
        if agent_recommendations.get("ad_offset"):
            config["ad_offset"] = agent_recommendations["ad_offset"]
        
        if agent_recommendations.get("creative_preferences"):
            creative_prefs = agent_recommendations["creative_preferences"]
            if creative_prefs.get("max_headline_chars"):
                config["max_headline_chars"] = creative_prefs["max_headline_chars"]
            if creative_prefs.get("image_enabled") is not None:
                config["image_enabled"] = creative_prefs["image_enabled"]
        
        if agent_recommendations.get("experiment_tag"):
            config["experiment_tag"] = agent_recommendations["experiment_tag"]
        
        return config