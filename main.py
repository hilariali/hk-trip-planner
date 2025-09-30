import streamlit as st
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import logging

from services.llm_orchestrator import get_llm_orchestrator, LLMRequest

@dataclass
class ChatMessage:
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    message_type: str = "text"  # "text", "itinerary", "system"

def initialize_session_state():
    """Initialize session state variables for the chat interface."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_msg = ChatMessage(
            role="assistant",
            content="👋 Welcome to HK Travel Planner! I'm your AI travel assistant specialized in creating accessible Hong Kong itineraries for families and seniors.\n\nTell me about your travel plans - who's traveling, any accessibility needs, dietary preferences, budget, and how many days you'll be visiting Hong Kong.",
            timestamp=datetime.now(),
            message_type="system"
        )
        st.session_state.messages.append(welcome_msg)
    
    if "conversation_context" not in st.session_state:
        st.session_state.conversation_context = {
            "user_preferences": {},
            "current_itinerary": None,
            "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "conversation_history": []
        }
    
    if "llm_orchestrator" not in st.session_state:
        st.session_state.llm_orchestrator = get_llm_orchestrator()

def display_chat_message(message: ChatMessage):
    """Display a chat message with appropriate styling."""
    with st.chat_message(message.role):
        if message.message_type == "system":
            st.markdown(f"🤖 **System**: {message.content}")
        elif message.message_type == "itinerary":
            st.markdown("📋 **Generated Itinerary**")
            st.markdown(message.content)
        else:
            st.markdown(message.content)
        
        # Show timestamp for debugging (can be removed in production)
        with st.expander("Message Details", expanded=False):
            st.caption(f"Time: {message.timestamp.strftime('%H:%M:%S')} | Type: {message.message_type}")

def add_message(role: str, content: str, message_type: str = "text"):
    """Add a new message to the conversation."""
    message = ChatMessage(
        role=role,
        content=content,
        timestamp=datetime.now(),
        message_type=message_type
    )
    st.session_state.messages.append(message)

def main():
    st.set_page_config(
        page_title="HK Travel Planner",
        page_icon="🏙️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("🏙️ HK Travel Planner")
    st.markdown("*AI-powered accessible travel planning for Hong Kong*")
    
    # Sidebar with session info and controls
    with st.sidebar:
        st.header("Session Info")
        if st.session_state.get("conversation_context"):
            st.write(f"**Session ID**: {st.session_state.conversation_context['session_id']}")
            st.write(f"**Messages**: {len(st.session_state.messages)}")
        
        st.divider()
        
        # Quick actions
        st.header("Quick Actions")
        if st.button("🔄 New Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_context = {
                "user_preferences": {},
                "current_itinerary": None,
                "session_id": f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            }
            st.rerun()
        
        if st.button("💾 Export Chat"):
            # TODO: Implement export functionality
            st.info("Export functionality coming soon!")
        
        st.divider()
        
        # System status
        st.header("System Status")
        st.success("✅ Chat Interface: Active")
        
        # Check LLM status
        if st.session_state.get("llm_orchestrator") and st.session_state.llm_orchestrator.is_available():
            st.success("✅ LLM Service: Connected")
            if st.button("🧪 Test LLM"):
                with st.spinner("Testing LLM connection..."):
                    test_response = st.session_state.llm_orchestrator.test_connection()
                    if test_response.success:
                        st.success(f"✅ LLM Test: {test_response.content}")
                    else:
                        st.error(f"❌ LLM Test Failed: {test_response.error_message}")
        else:
            st.error("❌ LLM Service: Not Connected")
        
        st.warning("⚠️ Data Sources: Not Connected")
    
    # Initialize session state
    initialize_session_state()
    
    # Display chat messages
    for message in st.session_state.messages:
        display_chat_message(message)
    
    # Chat input
    if prompt := st.chat_input("Describe your Hong Kong travel plans..."):
        # Add user message
        add_message("user", prompt)
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process user input (placeholder for now)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # TODO: Replace with actual LLM processing
                response = process_user_message(prompt)
                st.markdown(response)
                add_message("assistant", response)

def process_user_message(user_input: str) -> str:
    """Process user message and generate response using LLM."""
    
    # Update conversation history
    st.session_state.conversation_context["conversation_history"].append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now().isoformat()
    })
    
    # Get LLM orchestrator
    llm = st.session_state.llm_orchestrator
    
    if not llm.is_available():
        return "I'm sorry, but the AI service is currently unavailable. Please check the system status in the sidebar and try again later."
    
    # Create system prompt for conversation
    system_prompt = """You are an expert Hong Kong travel planner specializing in accessible tourism for families and seniors.

Your expertise includes:
- Accessibility features of Hong Kong attractions, restaurants, and transportation
- Mobility considerations (wheelchairs, elevators, step-free access)
- Dietary accommodations (soft meals, vegetarian, halal, allergies)
- Budget-conscious planning with senior and child discounts
- Safe, comfortable itineraries with appropriate pacing

Guidelines:
1. Be conversational and helpful
2. Ask clarifying questions to understand specific needs
3. Provide practical, actionable advice
4. Always consider accessibility and safety first
5. Suggest 2-3 venues per day maximum to prevent fatigue
6. Include cost estimates when possible
7. Explain your reasoning for recommendations

If the user provides complete travel requirements, offer to generate a detailed itinerary."""
    
    # Create LLM request
    request = LLMRequest(
        user_message=user_input,
        context=st.session_state.conversation_context,
        system_prompt=system_prompt,
        response_format="text",
        max_tokens=1500
    )
    
    # Get response from LLM
    response = llm.process_message(request)
    
    if response.success:
        # Update conversation history
        st.session_state.conversation_context["conversation_history"].append({
            "role": "assistant",
            "content": response.content,
            "timestamp": datetime.now().isoformat()
        })
        return response.content
    else:
        return f"I encountered an issue: {response.error_message}. Please try rephrasing your message or check the system status."

if __name__ == "__main__":
    main()