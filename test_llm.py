#!/usr/bin/env python3
"""Test script for LLM integration."""

import sys
import logging
from services.llm_orchestrator import get_llm_orchestrator, LLMRequest

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_llm_connection():
    """Test the LLM connection and basic functionality."""
    print("🧪 Testing LLM Connection...")
    
    # Initialize orchestrator
    llm = get_llm_orchestrator()
    
    if not llm.is_available():
        print("❌ LLM service is not available")
        return False
    
    print("✅ LLM orchestrator initialized")
    
    # Test basic connection
    print("\n🔍 Testing basic connection...")
    test_response = llm.test_connection()
    
    if test_response.success:
        print(f"✅ Connection test successful!")
        print(f"Response: {test_response.content}")
        print(f"Response time: {test_response.response_time:.2f}s")
        if test_response.tokens_used:
            print(f"Tokens used: {test_response.tokens_used}")
    else:
        print(f"❌ Connection test failed: {test_response.error_message}")
        return False
    
    # Test travel planning conversation
    print("\n🏙️ Testing travel planning conversation...")
    
    travel_request = LLMRequest(
        user_message="I'm planning a 2-day Hong Kong trip for my elderly parents who use wheelchairs. They prefer soft meals and have a budget of $200 per day. Can you help?",
        context={"conversation_history": []},
        system_prompt="You are a Hong Kong travel expert specializing in accessible tourism. Provide helpful, practical advice for travelers with mobility needs.",
        max_tokens=800
    )
    
    travel_response = llm.process_message(travel_request)
    
    if travel_response.success:
        print("✅ Travel planning test successful!")
        print(f"Response length: {len(travel_response.content)} characters")
        print(f"Response time: {travel_response.response_time:.2f}s")
        print("\n📝 Sample response:")
        print("-" * 50)
        print(travel_response.content[:500] + "..." if len(travel_response.content) > 500 else travel_response.content)
        print("-" * 50)
    else:
        print(f"❌ Travel planning test failed: {travel_response.error_message}")
        return False
    
    print("\n🎉 All tests passed! LLM integration is working correctly.")
    return True

if __name__ == "__main__":
    success = test_llm_connection()
    sys.exit(0 if success else 1)