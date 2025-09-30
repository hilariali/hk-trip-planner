#!/usr/bin/env python3
"""
Test Streamlit secrets configuration
"""

import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_secrets():
    """Test if Streamlit secrets are properly configured"""
    st.title("🔐 Streamlit Secrets Test")
    
    try:
        # Check if secrets are available
        if hasattr(st, 'secrets'):
            st.success("✅ Streamlit secrets are available")
            
            # Check AI configuration
            if 'ai' in st.secrets:
                st.success("✅ AI section found in secrets")
                
                # Check API key (without displaying it)
                if 'api_key' in st.secrets.ai:
                    api_key = st.secrets.ai.api_key
                    if api_key and api_key != "your-api-key-here":
                        st.success("✅ API key is configured")
                        st.info(f"API key length: {len(api_key)} characters")
                        st.info(f"API key starts with: {api_key[:8]}...")
                    else:
                        st.warning("⚠️ API key not set or still using placeholder")
                else:
                    st.error("❌ API key not found in secrets")
                
                # Show other configuration
                if 'base_url' in st.secrets.ai:
                    st.info(f"Base URL: {st.secrets.ai.base_url}")
                if 'model' in st.secrets.ai:
                    st.info(f"Model: {st.secrets.ai.model}")
                    
            else:
                st.error("❌ AI section not found in secrets")
                st.info("Make sure your .streamlit/secrets.toml has an [ai] section")
        else:
            st.error("❌ Streamlit secrets not available")
            
    except Exception as e:
        st.error(f"❌ Error accessing secrets: {str(e)}")
    
    # Test AI service integration
    st.subheader("🤖 AI Service Integration Test")
    
    if st.button("Test AI Service with Secrets"):
        try:
            from services.ai_venue_service import AIVenueService
            
            # Create AI service (should auto-load from secrets)
            ai_service = AIVenueService()
            stats = ai_service.get_service_stats()
            
            st.json(stats)
            
            if stats['client_available']:
                st.success("🎉 AI service is ready with your API key!")
                
                # Test venue generation
                if st.button("Generate Test Venues"):
                    with st.spinner("Generating AI venues..."):
                        test_preferences = {
                            'family_composition': {'adults': 2, 'seniors': 1},
                            'mobility_needs': ['wheelchair'],
                            'budget_range': (300, 800),
                            'trip_duration': 2
                        }
                        
                        venues = ai_service.generate_venues_for_preferences(test_preferences)
                        
                        if venues:
                            st.success(f"✅ Generated {len(venues)} AI venues!")
                            for venue in venues:
                                st.write(f"- **{venue['name']}** ({venue['category']})")
                                st.write(f"  {venue['description'][:100]}...")
                        else:
                            st.warning("No venues generated - check API key and connection")
            else:
                st.warning("AI service not ready - check API key configuration")
                
        except Exception as e:
            st.error(f"AI service test failed: {str(e)}")

if __name__ == "__main__":
    test_secrets()