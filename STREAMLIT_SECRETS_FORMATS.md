# 🔐 Streamlit Secrets Format Guide

## Issue: "No 'ai' section found in Streamlit secrets"

Try these different formats in your Streamlit Cloud secrets:

## Format 1: Standard Format (Recommended)
```toml
[ai]
api_key = "sk-your-actual-api-key-here"
base_url = "https://chatapi.akash.network/api/v1"
model = "Meta-Llama-3-1-8B-Instruct-FP8"
```

## Format 2: Alternative Section Names
```toml
[AI]
api_key = "sk-your-actual-api-key-here"
```

Or:
```toml
[openai]
api_key = "sk-your-actual-api-key-here"
```

## Format 3: Direct Key (Fallback)
```toml
AI_API_KEY = "sk-your-actual-api-key-here"
OPENAI_API_KEY = "sk-your-actual-api-key-here"
```

## Format 4: Simple Format
```toml
api_key = "sk-your-actual-api-key-here"
```

## Troubleshooting Steps:

### 1. Check Streamlit Cloud Dashboard
- Go to your app settings
- Find "Secrets" section
- Make sure the content is saved properly

### 2. Restart Your App
- In Streamlit Cloud, click "Reboot app"
- Wait for full restart

### 3. Test with Debug Tool
Run: `streamlit run debug_secrets.py`

### 4. Check Format
Make sure:
- No extra spaces
- Quotes around the API key
- Proper TOML syntax
- No special characters in section names

### 5. Alternative: Use Environment Variables
If secrets don't work, you can also set:
```
AI_API_KEY = "sk-your-actual-api-key-here"
```
In the Streamlit Cloud environment variables section.

## Current Status
The app now checks for API keys in this order:
1. `st.secrets.ai.api_key`
2. `st.secrets.AI.api_key` 
3. `st.secrets.openai.api_key`
4. `st.secrets.OPENAI.api_key`
5. Environment variable `AI_API_KEY`
6. Environment variable `OPENAI_API_KEY`

Try the debug tool to see exactly what's happening!