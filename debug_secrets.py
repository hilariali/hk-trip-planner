#!/usr/bin/env python3
"""
Debug Streamlit secrets configuration
"""

import streamlit as st
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_streamlit_secrets():
    """Debug Streamlit secrets step by step"""
    st.title("🔍 Streamlit Secrets Debugger")
    
    st.markdown("This tool helps debug Streamlit secrets configuration issues.")
    
    # Check if we're in Streamlit context
    try:
        st.write("✅ Running in Streamlit context")
        
        # Check if secrets attribute exists
        if hasattr(st, 'secrets'):
            st.success("✅ `st.secrets` attribute exists")
            
            # Show all available secrets (without values)
            try:
                secrets_keys = list(st.secrets.keys())
                st.info(f"Available secret sections: {secrets_keys}")
                
                if not secrets_keys:
                    st.warning("⚠️ No secrets found at all")
                    st.markdown("""
                    **Possible solutions:**
                    1. Check if you saved the secrets in Streamlit Cloud
                    2. Restart your Streamlit app
                    3. Check the secrets format in your dashboard
                    """)
                
                # Check specifically for 'ai' section
                if 'ai' in st.secrets:
                    st.success("✅ 'ai' section found in secrets!")
                    
                    # Check ai subsections (without showing values)
                    ai_keys = list(st.secrets.ai.keys())
                    st.info(f"Keys in 'ai' section: {ai_keys}")
                    
                    # Check api_key specifically
                    if 'api_key' in st.secrets.ai:
                        api_key = st.secrets.ai.api_key
                        if api_key and len(api_key.strip()) > 0:
                            st.success(f"✅ API key found (length: {len(api_key)})")
                            st.info(f"API key starts with: {api_key[:8]}...")
                        else:
                            st.error("❌ API key is empty")
                    else:
                        st.error("❌ 'api_key' not found in ai section")
                        
                else:
                    st.error("❌ 'ai' section NOT found in secrets")
                    st.markdown("""
                    **Your secrets should look like this:**
                    ```toml
                    [ai]
                    api_key = "sk-your-actual-key-here"
                    base_url = "https://chatapi.akash.network/api/v1"
                    model = "Meta-Llama-3-1-8B-Instruct-FP8"
                    ```
                    """)
                
            except Exception as e:
                st.error(f"Error reading secrets: {str(e)}")
                
        else:
            st.error("❌ `st.secrets` attribute not found")
            
    except Exception as e:
        st.error(f"Error in Streamlit context: {str(e)}")
    
    # Test AI service
    st.subheader("🤖 AI Service Test")
    
    if st.button("Test AI Service"):
        try:
            from services.ai_venue_service import AIVenueService
            
            with st.spinner("Testing AI service..."):
                ai_service = AIVenueService()
                stats = ai_service.get_service_stats()
                
                st.json(stats)
                
                if stats['client_available']:
                    st.success("🎉 AI service is working!")
                else:
                    st.warning("⚠️ AI service not available")
                    
        except Exception as e:
            st.error(f"AI service test failed: {str(e)}")
    
    # Manual secrets input for testing
    st.subheader("🔧 Manual Test")
    st.markdown("If secrets aren't working, you can test manually:")
    
    manual_key = st.text_input("Enter API key for testing", type="password")
    if st.button("Test Manual Key") and manual_key:
        try:
            from services.ai_venue_service import AIVenueService
            
            ai_service = AIVenueService(manual_key)
            stats = ai_service.get_service_stats()
            
            st.json(stats)
            
            if stats['client_available']:
                st.success("🎉 Manual API key works!")
            else:
                st.warning("⚠️ Manual API key not working")
                
        except Exception as e:
            st.error(f"Manual test failed: {str(e)}")

if __name__ == "__main__":
    debug_streamlit_secrets()