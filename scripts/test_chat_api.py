"""
Test LLM Chat API

Tests the chat API with different models and agents.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_list_agents():
    """Test listing available agents."""
    print("=" * 60)
    print("Testing: List Agents")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/chat/agents")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_list_models():
    """Test listing available models."""
    print("=" * 60)
    print("Testing: List Models")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/chat/models")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_chat_general():
    """Test chat with general assistant."""
    print("=" * 60)
    print("Testing: Chat with General Assistant")
    print("=" * 60)
    
    request = {
        "message": "What is the SIGNAL platform?",
        "model": "gpt-3.5-turbo",
        "agent": "general"
    }
    
    response = requests.post(f"{BASE_URL}/chat/chat", json=request)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_chat_bid_strategy():
    """Test chat with bid strategy agent."""
    print("=" * 60)
    print("Testing: Chat with Bid Strategy Agent")
    print("=" * 60)
    
    request = {
        "message": "Should I increase my bid for the Summer Training campaign?",
        "model": "gpt-3.5-turbo",
        "agent": "bid_strategy"
    }
    
    response = requests.post(f"{BASE_URL}/chat/chat", json=request)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()


def test_conversation_history():
    """Test conversation history."""
    print("=" * 60)
    print("Testing: Conversation History")
    print("=" * 60)
    
    # First message
    request1 = {
        "message": "What's the ROAS target for Gymshark?",
        "model": "gpt-3.5-turbo",
        "agent": "general"
    }
    
    response1 = requests.post(f"{BASE_URL}/chat/chat", json=request1)
    conversation_id = response1.json()["conversation_id"]
    print(f"First message - Conversation ID: {conversation_id}")
    print(f"Response: {response1.json()['response']}")
    print()
    
    # Second message in same conversation
    request2 = {
        "message": "What about CPA target?",
        "model": "gpt-3.5-turbo",
        "agent": "general",
        "conversation_id": conversation_id
    }
    
    response2 = requests.post(f"{BASE_URL}/chat/chat", json=request2)
    print(f"Second message - Conversation ID: {conversation_id}")
    print(f"Response: {response2.json()['response']}")
    print(f"Message count: {response2.json()['message_count']}")
    print()
    
    # Get full conversation
    response3 = requests.get(f"{BASE_URL}/chat/conversations/{conversation_id}")
    print(f"Full conversation:")
    print(json.dumps(response3.json(), indent=2))
    print()


def test_switch_agent():
    """Test switching agents in a conversation."""
    print("=" * 60)
    print("Testing: Switch Agent")
    print("=" * 60)
    
    # Start with general agent
    request1 = {
        "message": "Hello",
        "model": "gpt-3.5-turbo",
        "agent": "general"
    }
    
    response1 = requests.post(f"{BASE_URL}/chat/chat", json=request1)
    conversation_id = response1.json()["conversation_id"]
    print(f"Started with general agent")
    print()
    
    # Switch to bid strategy agent
    response2 = requests.post(
        f"{BASE_URL}/chat/conversations/{conversation_id}/agent",
        json={"agent": "bid_strategy"}
    )
    print(f"Switched to bid_strategy agent")
    print(json.dumps(response2.json(), indent=2))
    print()
    
    # Send message to new agent
    request2 = {
        "message": "Should I bid £3000 on Meta?",
        "model": "gpt-3.5-turbo",
        "agent": "bid_strategy",
        "conversation_id": conversation_id
    }
    
    response3 = requests.post(f"{BASE_URL}/chat/chat", json=request2)
    print(f"Message to bid_strategy agent:")
    print(f"Response: {response3.json()['response']}")
    print()


def main():
    """Run all tests."""
    print("LLM Chat API Test Suite")
    print("=" * 60)
    print()
    
    try:
        # Test listing endpoints
        test_list_agents()
        test_list_models()
        
        # Test chat with different agents (requires OPENAI_API_KEY)
        print("Note: Chat tests require OPENAI_API_KEY to be set")
        print("Skipping chat tests if API key not configured...")
        print()
        
        # Uncomment to test chat functionality
        # test_chat_general()
        # test_chat_bid_strategy()
        # test_conversation_history()
        # test_switch_agent()
        
        print("=" * 60)
        print("Test Suite Complete")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API server")
        print("Make sure the server is running: make server")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()