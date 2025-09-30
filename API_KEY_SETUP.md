# 🔑 API Key Setup Guide

## Quick Setup Options

### **Option 1: Through the App (Easiest)**
1. Run: `streamlit run app.py`
2. Look for "🤖 AI-Powered Recommendations" section
3. Enter your API key in the password field
4. Click "Configure AI Service"

### **Option 2: Environment File (Recommended for Development)**
1. Edit the `.env` file in your project root:
```bash
AI_API_KEY=sk-your-actual-api-key-here
```

2. Restart the app - it will automatically load the key

### **Option 3: Streamlit Secrets (For Production)**
1. Edit `.streamlit/secrets.toml`:
```toml
[ai]
api_key = "sk-your-actual-api-key-here"
```

2. For Streamlit Cloud, add this in your app's secrets section

## Your API Key Format
Based on your example, it should look like:
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## Test Your Setup
After adding the key, test it:
```bash
python3 test_ai_service.py
```

Or in the app, click "Test AI Service" button.

## What Happens When Key is Added
- ✅ AI generates personalized Hong Kong venues
- ✅ Weather-aware recommendations  
- ✅ Accessibility-optimized suggestions
- ✅ Budget-conscious venue selection
- ✅ Real Hong Kong locations with coordinates

## Security Notes
- ✅ `.env` file is in `.gitignore` (not committed to git)
- ✅ Streamlit secrets are secure
- ✅ App UI uses password field (hidden input)
- ✅ Keys are never logged or displayed

## Need Help?
The app works perfectly without the API key (uses 31 curated venues). Adding the key just enables unlimited AI-generated personalized recommendations!