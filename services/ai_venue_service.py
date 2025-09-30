"""
AI-Powered Venue Service for Hong Kong Trip Planner
Uses LLM API to generate dynamic, contextual venue recommendations
"""

import json
import logging
from typing import List, Dict, Optional
from datetime import datetime
from models import Venue, VenueCategory, Location, AccessibilityInfo, DietaryOption, WeatherSuitability

# Optional import for OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

# Configure logging
logger = logging.getLogger('services.ai_venue_service')

class AIVenueService:
    """Service for AI-generated venue recommendations"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI venue service"""
        self.version = "2025-09-30-ai-v1"
        self.api_key = api_key
        self.client = None
        self._cache = {}
        self._cache_expiry = {}
        
        if api_key:
            self._initialize_client(api_key)
        
        logger.info(f"AIVenueService initialized - Version: {self.version}")
    
    def _initialize_client(self, api_key: str):
        """Initialize OpenAI client with custom endpoint"""
        if not OPENAI_AVAILABLE:
            logger.warning("OpenAI library not available - install with: pip install openai")
            self.client = None
            return
            
        try:
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://chatapi.akash.network/api/v1"
            )
            logger.info("AI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {str(e)}")
            self.client = None
    
    def set_api_key(self, api_key: str):
        """Set API key and initialize client"""
        self.api_key = api_key
        self._initialize_client(api_key)
    
    def generate_venues_for_preferences(self, preferences: Dict, weather_data: Dict = None) -> List[Dict]:
        """Generate venue recommendations based on user preferences"""
        if not self.client:
            logger.warning("AI client not available - using fallback data")
            return self._get_fallback_venues()
        
        try:
            # Create context-aware prompt
            prompt = self._create_venue_prompt(preferences, weather_data)
            
            # Check cache first
            cache_key = self._get_cache_key(prompt)
            if self._is_cache_valid(cache_key):
                logger.info("Using cached AI venue recommendations")
                return self._cache[cache_key]
            
            # Generate new recommendations
            response = self.client.chat.completions.create(
                model="Meta-Llama-3-1-8B-Instruct-FP8",
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Parse AI response
            ai_content = response.choices[0].message.content
            venues = self._parse_ai_response(ai_content)
            
            # Cache the results
            self._cache[cache_key] = venues
            self._cache_expiry[cache_key] = datetime.now().timestamp() + 3600  # 1 hour cache
            
            logger.info(f"Generated {len(venues)} AI venue recommendations")
            return venues
            
        except Exception as e:
            logger.error(f"AI venue generation failed: {str(e)}")
            return self._get_fallback_venues()
    
    def generate_contextual_attractions(self, district: str = None, interests: List[str] = None) -> List[Dict]:
        """Generate attractions for specific district or interests"""
        if not self.client:
            return self._get_fallback_venues()
        
        try:
            prompt = f"""Generate 5 Hong Kong attractions for:
District: {district or 'Any'}
Interests: {', '.join(interests) if interests else 'General tourism'}

Include accessibility information and practical details."""
            
            response = self.client.chat.completions.create(
                model="Meta-Llama-3-1-8B-Instruct-FP8",
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            venues = self._parse_ai_response(response.choices[0].message.content)
            logger.info(f"Generated {len(venues)} contextual attractions")
            return venues
            
        except Exception as e:
            logger.error(f"Contextual attraction generation failed: {str(e)}")
            return []
    
    def enhance_venue_descriptions(self, venues: List[Dict]) -> List[Dict]:
        """Enhance existing venues with AI-generated descriptions"""
        if not self.client or not venues:
            return venues
        
        try:
            venue_names = [v.get('name', 'Unknown') for v in venues[:5]]  # Limit to 5 for API efficiency
            
            prompt = f"""Enhance these Hong Kong venues with engaging descriptions and accessibility tips:
{', '.join(venue_names)}

For each venue, provide:
1. Engaging 2-sentence description
2. Accessibility highlights
3. Best visiting tips for seniors/families"""
            
            response = self.client.chat.completions.create(
                model="Meta-Llama-3-1-8B-Instruct-FP8",
                messages=[
                    {"role": "system", "content": "You are a Hong Kong tourism expert specializing in accessible travel."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            # Parse and apply enhancements
            enhanced_info = self._parse_enhancement_response(response.choices[0].message.content)
            return self._apply_enhancements(venues, enhanced_info)
            
        except Exception as e:
            logger.error(f"Venue enhancement failed: {str(e)}")
            return venues
    
    def _create_venue_prompt(self, preferences: Dict, weather_data: Dict = None) -> str:
        """Create contextual prompt for venue generation"""
        family_comp = preferences.get('family_composition', {})
        mobility_needs = preferences.get('mobility_needs', [])
        dietary_restrictions = preferences.get('dietary_restrictions', [])
        budget_range = preferences.get('budget_range', (200, 800))
        duration = preferences.get('trip_duration', 3)
        
        weather_context = ""
        if weather_data:
            temp = weather_data.get('temperature', 25)
            rainfall = weather_data.get('rainfall_probability', 20)
            weather_context = f"Current weather: {temp}°C, {rainfall}% rain chance. "
        
        prompt = f"""Generate {min(duration * 3, 10)} Hong Kong venues for a {duration}-day trip:

Family: {family_comp.get('adults', 2)} adults, {family_comp.get('children', 0)} children, {family_comp.get('seniors', 0)} seniors
Budget: HKD {budget_range[0]}-{budget_range[1]} per person per day
Accessibility needs: {', '.join(mobility_needs) if mobility_needs else 'None'}
Dietary needs: {', '.join(dietary_restrictions) if dietary_restrictions else 'None'}
{weather_context}

Include mix of attractions, restaurants, and transport. Focus on accessibility and senior-friendly options."""
        
        return prompt
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for AI venue generation"""
        return """You are a Hong Kong tourism expert specializing in accessible travel for families and seniors.

Generate venue recommendations in this EXACT JSON format:
[
  {
    "id": "ai_001",
    "name": "Venue Name",
    "category": "attraction|restaurant|transport|museum|park|shopping",
    "description": "Detailed description with accessibility highlights",
    "district": "Hong Kong district name",
    "address": "Full address",
    "latitude": 22.xxxx,
    "longitude": 114.xxxx,
    "cost_range": [min_cost, max_cost],
    "accessibility": {
      "wheelchair_accessible": true/false,
      "has_elevator": true/false,
      "accessible_toilets": true/false,
      "step_free_access": true/false,
      "notes": ["accessibility note 1", "note 2"]
    },
    "dietary_options": {
      "soft_meals": true/false,
      "vegetarian": true/false,
      "halal": true/false,
      "notes": ["dietary note 1"]
    },
    "elderly_friendly": true/false,
    "weather_suitability": "indoor|outdoor|mixed",
    "opening_hours": "Daily 09:00-18:00",
    "phone": "+852 xxxx xxxx",
    "website": "https://example.com"
  }
]

IMPORTANT: 
- Use real Hong Kong locations with accurate coordinates
- Provide practical accessibility information
- Include cost estimates in HKD
- Focus on senior and family-friendly venues
- Return ONLY valid JSON, no other text"""
    
    def _parse_ai_response(self, content: str) -> List[Dict]:
        """Parse AI response into venue data"""
        try:
            # Clean the response
            content = content.strip()
            
            # Find JSON content
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON found in AI response")
                return []
            
            json_content = content[start_idx:end_idx]
            venues = json.loads(json_content)
            
            # Validate and clean venue data
            validated_venues = []
            for venue in venues:
                if self._validate_venue_data(venue):
                    validated_venues.append(venue)
            
            return validated_venues
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return []
    
    def _validate_venue_data(self, venue: Dict) -> bool:
        """Validate venue data structure"""
        required_fields = ['name', 'category', 'description']
        
        for field in required_fields:
            if not venue.get(field):
                return False
        
        # Ensure valid category
        valid_categories = ['attraction', 'restaurant', 'transport', 'museum', 'park', 'shopping']
        if venue.get('category') not in valid_categories:
            venue['category'] = 'attraction'
        
        # Ensure cost_range is valid
        if not venue.get('cost_range') or len(venue['cost_range']) != 2:
            venue['cost_range'] = [0, 100]
        
        # Ensure coordinates are reasonable for Hong Kong
        lat = venue.get('latitude', 22.3)
        lng = venue.get('longitude', 114.2)
        if not (22.1 <= lat <= 22.6 and 113.8 <= lng <= 114.5):
            venue['latitude'] = 22.3
            venue['longitude'] = 114.2
        
        return True
    
    def _parse_enhancement_response(self, content: str) -> Dict:
        """Parse venue enhancement response"""
        # Simple parsing for enhancement text
        enhancements = {}
        lines = content.split('\n')
        current_venue = None
        
        for line in lines:
            line = line.strip()
            if ':' in line and any(word in line.lower() for word in ['venue', 'attraction', 'restaurant']):
                current_venue = line.split(':')[0].strip()
                enhancements[current_venue] = {'description': '', 'tips': []}
            elif current_venue and line:
                if 'accessibility' in line.lower() or 'tip' in line.lower():
                    enhancements[current_venue]['tips'].append(line)
                else:
                    enhancements[current_venue]['description'] += line + ' '
        
        return enhancements
    
    def _apply_enhancements(self, venues: List[Dict], enhancements: Dict) -> List[Dict]:
        """Apply AI enhancements to venues"""
        for venue in venues:
            venue_name = venue.get('name', '')
            for enhanced_name, enhancement in enhancements.items():
                if enhanced_name.lower() in venue_name.lower():
                    if enhancement.get('description'):
                        venue['description'] = enhancement['description'].strip()
                    if enhancement.get('tips'):
                        venue.setdefault('accessibility', {})['notes'] = enhancement['tips']
                    break
        
        return venues
    
    def _get_cache_key(self, prompt: str) -> str:
        """Generate cache key for prompt"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cache entry is still valid"""
        if cache_key not in self._cache:
            return False
        
        expiry_time = self._cache_expiry.get(cache_key, 0)
        return datetime.now().timestamp() < expiry_time
    
    def _get_fallback_venues(self) -> List[Dict]:
        """Get fallback venues when AI is not available"""
        return [
            {
                "id": "ai_fallback_1",
                "name": "Victoria Peak Sky Terrace",
                "category": "attraction",
                "description": "Hong Kong's premier viewing destination with panoramic city views and accessible facilities.",
                "district": "Central and Western",
                "address": "The Peak, Hong Kong Island",
                "latitude": 22.2711,
                "longitude": 114.1489,
                "cost_range": [65, 100],
                "accessibility": {
                    "wheelchair_accessible": True,
                    "has_elevator": True,
                    "accessible_toilets": True,
                    "step_free_access": True,
                    "notes": ["Peak Tram wheelchair accessible", "Sky Terrace has elevator access"]
                },
                "elderly_friendly": True,
                "weather_suitability": "mixed"
            },
            {
                "id": "ai_fallback_2",
                "name": "Dim Sum Square (Accessible)",
                "category": "restaurant",
                "description": "Traditional Cantonese dim sum restaurant with senior-friendly seating and soft meal options.",
                "district": "Central",
                "address": "Central District, Hong Kong Island",
                "latitude": 22.2816,
                "longitude": 114.1578,
                "cost_range": [150, 300],
                "accessibility": {
                    "wheelchair_accessible": True,
                    "has_elevator": True,
                    "accessible_toilets": True,
                    "step_free_access": True,
                    "notes": ["Ground floor seating available", "Staff assistance provided"]
                },
                "dietary_options": {
                    "soft_meals": True,
                    "vegetarian": True,
                    "notes": ["Steamed dim sum options", "Congee available"]
                },
                "elderly_friendly": True,
                "weather_suitability": "indoor"
            }
        ]
    
    def get_service_stats(self) -> Dict:
        """Get AI service statistics"""
        return {
            "version": self.version,
            "client_available": self.client is not None,
            "cache_entries": len(self._cache),
            "api_key_set": self.api_key is not None
        }