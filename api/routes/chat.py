"""
LLM Chat API Routes

Allows users to chat with different models and agents.
Supports conversation history and model/agent switching.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Literal
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from shared.database import get_async_session
from shared.utils.settings import settings
from services.common import agent_execution_logger

router = APIRouter(prefix="/chat", tags=["chat"])


# ============ MODELS ============

class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    message: str
    model: Literal["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"] = "gpt-4-turbo"
    agent: Optional[Literal[
        "bid_strategy",
        "content_brief",
        "creative_optimization",
        "market_analysis",
        "orchestration",
        "general"
    ]] = "general"
    conversation_id: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2048


class ChatResponse(BaseModel):
    response: str
    model: str
    agent: str
    conversation_id: str
    message_count: int
    tokens_used: Optional[int] = None


class Conversation(BaseModel):
    conversation_id: str
    agent: str
    model: str
    messages: List[ChatMessage]
    created_at: str
    updated_at: str


class AgentConfig(BaseModel):
    name: str
    description: str
    system_prompt: str
    capabilities: List[str]


# ============ AGENT CONFIGURATIONS ============

AGENT_CONFIGS = {
    "bid_strategy": AgentConfig(
        name="Bid Strategy Agent",
        description="Makes strategic bidding decisions for media buying",
        system_prompt="""You are the Bid Strategy Agent for the SIGNAL media trading platform. 

Your role is to:
- Analyze market conditions and competitive landscape
- Make strategic bidding decisions beyond algorithmic calculations
- Provide reasoning and risk assessment for bid decisions
- Suggest alternative strategies

When discussing bidding, always:
- Consider budget constraints and ROAS targets
- Provide confidence scores for your recommendations
- Explain the reasoning behind your decisions
- Consider platform-specific best practices""",
        capabilities=["Bid analysis", "Risk assessment", "Strategy recommendations"]
    ),
    "content_brief": AgentConfig(
        name="Content Brief Agent",
        description="Generates creative briefs based on gap analysis",
        system_prompt="""You are the Content Brief Generation Agent for the SIGNAL platform.

Your role is to:
- Analyze gap matrix results to identify content opportunities
- Generate creative briefs for high-priority gaps
- Ensure differentiation from competitor angles
- Tailor content to specific platforms and goals

When creating briefs, always:
- Include topic, angle, hook, proof point, and CTA
- Specify target audience and platform
- Provide confidence in your recommendations
- Ensure brand alignment""",
        capabilities=["Creative brief generation", "Gap analysis", "Differentiation strategy"]
    ),
    "creative_optimization": AgentConfig(
        name="Creative Optimization Agent",
        description="Analyzes and optimizes creative performance",
        system_prompt="""You are the Creative Optimization Agent for the SIGNAL platform.

Your role is to:
- Analyze creative performance data
- Identify strengths and weaknesses
- Suggest specific optimizations
- Generate creative variations for testing

When optimizing creatives, always:
- Analyze visual and copy elements
- Provide specific improvement suggestions
- Predict performance lift
- Consider platform-specific best practices""",
        capabilities=["Creative analysis", "Performance optimization", "A/B testing suggestions"]
    ),
    "market_analysis": AgentConfig(
        name="Market Analysis Agent",
        description="Analyzes market intelligence and provides strategic insights",
        system_prompt="""You are the Market Analysis Agent for the SIGNAL platform.

Your role is to:
- Analyze market intelligence from multiple sources
- Identify strategic opportunities and threats
- Provide competitive intelligence
- Generate actionable market insights

When analyzing markets, always:
- Provide evidence for your insights
- Assess urgency and actionability
- Consider competitive landscape
- Focus on actionable recommendations""",
        capabilities=["Market intelligence", "Competitive analysis", "Opportunity detection"]
    ),
    "orchestration": AgentConfig(
        name="Orchestration Agent",
        description="Central coordinator for all AI agents",
        system_prompt="""You are the Orchestration Agent for the SIGNAL platform.

Your role is to:
- Coordinate execution of specialized agents
- Manage agent priorities and dependencies
- Aggregate agent outputs into unified decisions
- Handle agent failures and fallbacks

When orchestrating, always:
- Consider agent priorities and dependencies
- Provide unified decisions from multiple inputs
- Handle errors gracefully with fallbacks
- Ensure system reliability""",
        capabilities=["Agent coordination", "Task prioritization", "Decision aggregation"]
    ),
    "general": AgentConfig(
        name="General Assistant",
        description="General-purpose AI assistant for the SIGNAL platform",
        system_prompt="""You are a helpful AI assistant for the SIGNAL media trading platform.

You can help with:
- Platform features and functionality
- Media buying best practices
- Marketing strategy questions
- Technical support

Always be helpful, accurate, and concise in your responses.""",
        capabilities=["General assistance", "Platform support", "Best practices"]
    )
}


# ============ CONVERSATION STORAGE ============

# In-memory conversation storage (in production, use database)
conversations: Dict[str, Conversation] = {}


def generate_conversation_id() -> str:
    """Generate a unique conversation ID."""
    return f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(datetime.now()) % 10000:04d}"


def get_agent_system_prompt(agent: str) -> str:
    """Get the system prompt for an agent."""
    if agent in AGENT_CONFIGS:
        return AGENT_CONFIGS[agent].system_prompt
    return AGENT_CONFIGS["general"].system_prompt


# ============ ENDPOINTS ============

@router.get("/agents")
async def list_agents():
    """List all available agents with their configurations."""
    return {
        "agents": [
            {
                "id": agent_id,
                "name": config.name,
                "description": config.description,
                "capabilities": config.capabilities
            }
            for agent_id, config in AGENT_CONFIGS.items()
        ]
    }


@router.get("/models")
async def list_models():
    """List all available models."""
    return {
        "models": [
            {"id": "gpt-4", "name": "GPT-4", "description": "Most capable model"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo", "description": "Fast and capable"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo", "description": "Fast and cost-effective"},
            {"id": "gpt-4o", "name": "GPT-4 Omni", "description": "Multimodal model"}
        ]
    }


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Send a chat message and get a response from the specified model and agent.
    
    Args:
        request: Chat request with message, model, agent, and conversation ID
        session: Database session
    
    Returns:
        Chat response with the agent's reply
    """
    
    # Check for OpenAI API key
    if not settings.openai_api_key:
        raise HTTPException(
            status_code=400,
            detail="OPENAI_API_KEY not configured. Please set OPENAI_API_KEY in environment."
        )
    
    # Get or create conversation
    if request.conversation_id:
        if request.conversation_id not in conversations:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation {request.conversation_id} not found"
            )
        conversation = conversations[request.conversation_id]
        
        # Update model/agent if changed
        conversation.model = request.model
        conversation.agent = request.agent
    else:
        conversation_id = generate_conversation_id()
        conversation = Conversation(
            conversation_id=conversation_id,
            agent=request.agent,
            model=request.model,
            messages=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        conversations[conversation_id] = conversation
    
    # Add user message
    user_message = ChatMessage(
        role="user",
        content=request.message,
        timestamp=datetime.now().isoformat()
    )
    conversation.messages.append(user_message)
    
    # Prepare messages for OpenAI
    system_prompt = get_agent_system_prompt(request.agent)
    
    messages_for_api = [
        {"role": "system", "content": system_prompt}
    ]
    
    # Add conversation history (last 10 messages to stay within context limits)
    recent_messages = conversation.messages[-10:] if len(conversation.messages) > 10 else conversation.messages
    for msg in recent_messages:
        messages_for_api.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Call OpenAI API
    import time
    start_time = time.time()
    
    try:
        from openai import OpenAI
        
        client = OpenAI(api_key=settings.openai_api_key)
        
        response = client.chat.completions.create(
            model=request.model,
            messages=messages_for_api,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        assistant_message_content = response.choices[0].message.content
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else None
        
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Calculate cost (rough estimate)
        cost_per_1k_tokens = {
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-3.5-turbo": 0.001,
            "gpt-4o": 0.005
        }
        cost_usd = (tokens_used / 1000) * cost_per_1k_tokens.get(request.model, 0.01) if tokens_used else 0
        
        # Log chat execution
        await agent_execution_logger.log_chat_execution(
            agent_name=request.agent,
            model=request.model,
            user_message=request.message,
            agent_response=assistant_message_content,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
            execution_time_ms=execution_time_ms,
            success=True
        )
        
    except Exception as e:
        execution_time_ms = int((time.time() - start_time) * 1000)
        
        # Log failed execution
        await agent_execution_logger.log_chat_execution(
            agent_name=request.agent,
            model=request.model,
            user_message=request.message,
            agent_response=str(e),
            tokens_used=0,
            cost_usd=0,
            execution_time_ms=execution_time_ms,
            success=False
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Error calling OpenAI API: {str(e)}"
        )
    
    # Add assistant response to conversation
    assistant_message = ChatMessage(
        role="assistant",
        content=assistant_message_content,
        timestamp=datetime.now().isoformat()
    )
    conversation.messages.append(assistant_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.now().isoformat()
    
    return ChatResponse(
        response=assistant_message_content,
        model=request.model,
        agent=request.agent,
        conversation_id=conversation_id,
        message_count=len(conversation.messages),
        tokens_used=tokens_used
    )


@router.get("/conversations")
async def list_conversations():
    """List all conversations."""
    return {
        "conversations": [
            {
                "conversation_id": conv_id,
                "agent": conv.agent,
                "model": conv.model,
                "message_count": len(conv.messages),
                "created_at": conv.created_at,
                "updated_at": conv.updated_at
            }
            for conv_id, conv in conversations.items()
        ]
    }


@router.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation by ID."""
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found"
        )
    
    conversation = conversations[conversation_id]
    
    return {
        "conversation_id": conversation.conversation_id,
        "agent": conversation.agent,
        "model": conversation.model,
        "messages": [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp
            }
            for msg in conversation.messages
        ],
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found"
        )
    
    del conversations[conversation_id]
    
    return {"message": f"Conversation {conversation_id} deleted"}


@router.post("/conversations/{conversation_id}/agent")
async def switch_agent(
    conversation_id: str,
    agent: Literal["bid_strategy", "content_brief", "creative_optimization", "market_analysis", "orchestration", "general"]
):
    """Switch the agent for a conversation."""
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found"
        )
    
    conversation = conversations[conversation_id]
    conversation.agent = agent
    conversation.updated_at = datetime.now().isoformat()
    
    return {
        "message": f"Switched to {agent}",
        "conversation_id": conversation_id,
        "new_agent": agent
    }


@router.post("/conversations/{conversation_id}/model")
async def switch_model(
    conversation_id: str,
    model: Literal["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o"]
):
    """Switch the model for a conversation."""
    if conversation_id not in conversations:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found"
        )
    
    conversation = conversations[conversation_id]
    conversation.model = model
    conversation.updated_at = datetime.now().isoformat()
    
    return {
        "message": f"Switched to {model}",
        "conversation_id": conversation_id,
        "new_model": model
    }