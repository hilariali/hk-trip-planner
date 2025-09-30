# 🤖 AI-Powered Hong Kong Trip Planner Setup Guide

## Overview
The Hong Kong Trip Planner now includes an AI-powered venue recommendation system that generates personalized suggestions based on user preferences, weather conditions, and accessibility needs.

## AI Service Features

### 🎯 **Contextual Recommendations**
- Generates venues based on family composition, budget, and accessibility needs
- Weather-aware suggestions (indoor/outdoor based on conditions)
- Senior and family-friendly focus
- Real Hong Kong locations with accurate coordinates

### 🏗️ **System Architecture**
```
User Preferences → AI Service → LLM API → Contextual Venues → Itinerary Engine
```

### 📊 **Data Sources (4-Layer Strategy)**
1. **Offline Data (13 venues)** - Always available foundation
2. **Local Database (6 venues)** - Original functionality  
3. **Government APIs (10+ venues)** - Real-time when available
4. **AI Generated (Dynamic)** - Personalized recommendations

## Setup Instructions

### 1. **API Configuration**
The system uses OpenAI-compatible APIs. Currently configured for:
- **Provider**: Akash Network
- **Endpoint**: `https://chatapi.akash.network/api/v1`
- **Model**: `Meta-Llama-3-1-8B-Instruct-FP8`

### 2. **Get API Key**
You mentioned you'll provide the API key later. The format should be:
```
sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. **Configure in App**
1. Open the Hong Kong Trip Planner
2. Expand "🤖 AI-Powered Recommendations" section
3. Enter your API key in the password field
4. Click "Configure AI Service"
5. Test with "Test AI Service" button

### 4. **Alternative Models**
The system can be easily adapted for other models:

#### **DeepSeek-V3**
```python
# Update in ai_venue_service.py
model="deepseek-chat"  # or specific DeepSeek model
```

#### **Other OpenAI-Compatible APIs**
```python
# Update base_url in ai_venue_service.py
base_url="https://your-api-endpoint.com/v1"
```

## Usage Examples

### **Basic Usage (No API Key)**
- System works with 29 curated venues
- Uses offline + government data
- Reliable fallback experience

### **AI-Enhanced Usage (With API Key)**
- Generates dynamic venues based on preferences
- Contextual recommendations
- Weather-aware suggestions
- Personalized accessibility features

### **Sample AI Prompt**
```
Generate 6 Hong Kong venues for a 2-day trip:

Family: 2 adults, 0 children, 1 seniors
Budget: HKD 300-800 per person per day
Accessibility needs: wheelchair, elevator_only
Dietary needs: soft_meals
Current weather: 25°C, 20% rain chance

Include mix of attractions, restaurants, and transport. 
Focus on accessibility and senior-friendly options.
```

### **Sample AI Response**
```json
[
  {
    "id": "ai_001",
    "name": "Hong Kong Museum of Art (Accessible Wing)",
    "category": "museum",
    "description": "World-class art museum with full wheelchair access and senior-friendly exhibits",
    "district": "Tsim Sha Tsui",
    "latitude": 22.2947,
    "longitude": 114.1694,
    "cost_range": [10, 30],
    "accessibility": {
      "wheelchair_accessible": true,
      "has_elevator": true,
      "accessible_toilets": true,
      "notes": ["Wheelchair loans available", "Audio guides for seniors"]
    },
    "elderly_friendly": true,
    "weather_suitability": "indoor"
  }
]
```

## Technical Details

### **Caching System**
- 1-hour cache for AI responses
- Reduces API calls and costs
- Improves response time

### **Error Handling**
- Graceful fallback to offline data
- Validates AI-generated venue data
- Ensures Hong Kong coordinate bounds
- Handles API failures transparently

### **Performance**
- Optional AI enhancement (doesn't break core functionality)
- Efficient prompt engineering
- Minimal API calls through caching

## Testing

### **Test Without API Key**
```bash
python3 test_ai_service.py
```

### **Test With API Key**
```python
from services.ai_venue_service import AIVenueService

ai_service = AIVenueService("your-api-key-here")
venues = ai_service.generate_venues_for_preferences({
    'family_composition': {'adults': 2, 'seniors': 1},
    'mobility_needs': ['wheelchair'],
    'budget_range': (300, 800),
    'trip_duration': 2
})
```

### **Integration Test**
```bash
python3 debug_test.py
```

## Benefits

### **For Users**
- ✅ **Personalized recommendations** based on specific needs
- ✅ **Weather-aware suggestions** for optimal planning
- ✅ **Accessibility-first approach** for seniors and families
- ✅ **Always works** even without AI (fallback system)

### **For Developers**
- ✅ **Modular design** - AI is optional enhancement
- ✅ **Easy model switching** - OpenAI-compatible interface
- ✅ **Comprehensive testing** - Multiple fallback layers
- ✅ **Cost efficient** - Caching and smart prompting

## Next Steps

1. **Provide API Key** - Enable full AI functionality
2. **Test Generation** - Verify personalized recommendations
3. **Monitor Usage** - Track API calls and performance
4. **Optimize Prompts** - Refine for better Hong Kong context

The system is ready for AI enhancement while maintaining full functionality without it! 🚀