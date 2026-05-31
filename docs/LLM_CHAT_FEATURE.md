# LLM Chat Feature

## Overview

The LLM Chat feature allows users to interact with different AI models and specialized agents through a conversational interface. Users can switch between agents, maintain conversation history, and get context-aware responses.

## Features

### Multiple Models
- **GPT-4**: Most capable model
- **GPT-4 Turbo**: Fast and capable
- **GPT-3.5 Turbo**: Fast and cost-effective
- **GPT-4 Omni**: Multimodal model

### Specialized Agents
- **Bid Strategy Agent**: Makes strategic bidding decisions
- **Content Brief Agent**: Generates creative briefs
- **Creative Optimization Agent**: Analyzes creative performance
- **Market Analysis Agent**: Provides market intelligence
- **Orchestration Agent**: Coordinates all agents
- **General Assistant**: General-purpose AI assistant

### Conversation Features
- **Conversation History**: Maintains full chat history
- **Agent Switching**: Switch agents mid-conversation
- **Model Switching**: Switch models mid-conversation
- **Context Awareness**: Agents remember conversation context
- **Token Usage Tracking**: Track token usage per request

## API Endpoints

### List Agents
```bash
GET /chat/agents
```

Lists all available agents with their configurations.

### List Models
```bash
GET /chat/models
```

Lists all available models.

### Send Chat Message
```bash
POST /chat/chat
Content-Type: application/json

{
  "message": "Should I increase my bid on Meta?",
  "model": "gpt-4-turbo",
  "agent": "bid_strategy",
  "conversation_id": "optional-conversation-id",
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### List Conversations
```bash
GET /chat/conversations
```

Lists all conversations.

### Get Conversation
```bash
GET /chat/conversations/{conversation_id}
```

Gets full conversation history.

### Delete Conversation
```bash
DELETE /chat/conversations/{conversation_id}
```

Deletes a conversation.

### Switch Agent
```bash
POST /chat/conversations/{conversation_id}/agent
Content-Type: application/json

{
  "agent": "bid_strategy"
}
```

### Switch Model
```bash
POST /chat/conversations/{conversation_id}/model
Content-Type: application/json

{
  "model": "gpt-4"
}
```

## Usage Examples

### Example 1: Chat with Bid Strategy Agent
```bash
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Should I bid £3000 on the Summer Training campaign?",
    "model": "gpt-4-turbo",
    "agent": "bid_strategy"
  }'
```

### Example 2: Multi-turn Conversation
```bash
# First message
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the SIGNAL platform?",
    "model": "gpt-3.5-turbo",
    "agent": "general"
  }'

# Response includes conversation_id: "conv_20250528_210419_1234"

# Second message with conversation history
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How does it optimize bids?",
    "model": "gpt-3.5-turbo",
    "agent": "general",
    "conversation_id": "conv_20250528_210419_1234"
  }'
```

### Example 3: Switch Agents Mid-Conversation
```bash
# Start with general agent
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello",
    "model": "gpt-3.5-turbo",
    "agent": "general"
  }'

# Switch to bid strategy agent
curl -X POST http://localhost:8000/chat/conversations/conv_1234/agent \
  -H "Content-Type: application/json" \
  -d '{"agent": "bid_strategy"}'

# Continue with bid strategy agent
curl -X POST http://localhost:8000/chat/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Should I bid £5000?",
    "model": "gpt-3.5-turbo",
    "agent": "bid_strategy",
    "conversation_id": "conv_1234"
  }'
```

## Agent System Prompts

Each agent has a specialized system prompt:

### Bid Strategy Agent
- Analyzes market conditions and competitive landscape
- Makes strategic bidding decisions
- Provides risk assessment
- Suggests alternative strategies

### Content Brief Agent
- Analyzes gap matrix results
- Generates creative briefs
- Ensures differentiation from competitors
- Tailors content to platforms

### Creative Optimization Agent
- Analyzes creative performance data
- Identifies strengths and weaknesses
- Suggests specific optimizations
- Generates creative variations

### Market Analysis Agent
- Analyzes market intelligence
- Identifies strategic opportunities
- Provides competitive intelligence
- Generates actionable insights

### Orchestration Agent
- Coordinates agent execution
- Manages priorities and dependencies
- Aggregates agent outputs
- Handles failures gracefully

## Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=sk-your-openai-key-here
```

### Optional Settings
- `temperature`: Controls randomness (0.0-2.0, default 0.7)
- `max_tokens`: Maximum response length (default 2048)

## Testing

Run the test script:
```bash
python3 scripts/test_chat_api.py
```

Or use the Makefile:
```bash
make test-chat-api
```

## Integration with AutoMann

The chat feature can be integrated with AutoMann (Autonomous Agent Management) for:
- **Agent Orchestration**: Automatically route queries to appropriate agents
- **Context Switching**: Dynamically switch agents based on conversation context
- **Multi-Agent Collaboration**: Enable multiple agents to collaborate on complex queries
- **AutoMann Integration**: Use AutoMann for autonomous agent selection and routing

## Future Enhancements

- **WebSocket Support**: Real-time streaming chat responses
- **Database Persistence**: Store conversations in database
- **RAG Integration**: Retrieve relevant documents for context
- **Tool Calling**: Enable agents to call external tools/APIs
- **Multi-Modal Support**: Support image and file uploads (with GPT-4o)
- **Agent Collaboration**: Enable multiple agents to respond to a single query
- **Conversation Analytics**: Track conversation patterns and outcomes

## Best Practices

1. **Choose the Right Agent**: Use specialized agents for domain-specific questions
2. **Use Conversation History**: Maintain context by using conversation_id
3. **Model Selection**: Use GPT-3.5-turbo for speed, GPT-4 for complex reasoning
4. **Temperature Settings**: Lower temperature (0.3-0.5) for factual responses, higher (0.7-1.0) for creative tasks
5. **Token Management**: Monitor token usage to manage costs

## Troubleshooting

### Error: OPENAI_API_KEY not configured
**Solution**: Set OPENAI_API_KEY in .env.local or environment variables

### Error: Conversation not found
**Solution**: Ensure conversation_id is valid and hasn't been deleted

### Error: Model not available
**Solution**: Check model ID matches available models (gpt-4, gpt-4-turbo, gpt-3.5-turbo, gpt-4o)

### Error: Agent not found
**Solution**: Use valid agent IDs: bid_strategy, content_brief, creative_optimization, market_analysis, orchestration, general