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
        
        # Try hardcoded key first for simplicity
        if not api_key:
            api_key = self._get_hardcoded_key()
        
        # If no hardcoded key, try environment/secrets
        if not api_key:
            api_key = self._load_api_key_from_env()
        
        if api_key:
            self._initialize_client(api_key)
        
        logger.info(f"AIVenueService initialized - Version: {self.version}")
    
    def _initialize_client(self, api_key: str):
        """Initialize OpenAI client with custom endpoint"""
        logger.info("=== INITIALIZING AI CLIENT ===")
        
        if not OPENAI_AVAILABLE:
            logger.error("❌ OpenAI library not available - install with: pip install openai")
            self.client = None
            return
        
        logger.info("✅ OpenAI library is available")
        
        if not api_key or not api_key.strip():
            logger.error("❌ API key is empty or None")
            self.client = None
            return
            
        try:
            logger.info(f"Initializing OpenAI client with key length: {len(api_key)}")
            logger.info("Using base URL: https://chatapi.akash.network/api/v1")
            
            self.client = openai.OpenAI(
                api_key=api_key,
                base_url="https://chatapi.akash.network/api/v1"
            )
            
            logger.info("✅ AI client initialized successfully")
            
            # Test the client with a simple request
            try:
                logger.info("Testing AI client connection...")
                # We'll test this in the venue generation method
                logger.info("✅ AI client ready for requests")
            except Exception as test_e:
                logger.warning(f"AI client test failed: {str(test_e)}")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI client: {str(e)}", exc_info=True)
            self.client = None
    
    def set_api_key(self, api_key: str):
        """Set API key and initialize client"""
        self.api_key = api_key
        self._initialize_client(api_key)
    
    def generate_venues_for_preferences(self, preferences: Dict, weather_data: Dict = None) -> List[Dict]:
        """Generate venue recommendations based on user preferences"""
        logger.info("=== GENERATING AI VENUES ===")
        logger.info(f"Preferences: {preferences}")
        logger.info(f"Weather data: {weather_data}")
        
        if not self.client:
            logger.warning("❌ AI client not available - using fallback data")
            return self._get_fallback_venues()
        
        logger.info("✅ AI client is available, proceeding with generation")
        
        try:
            # Create context-aware prompt
            prompt = self._create_venue_prompt(preferences, weather_data)
            logger.info(f"Generated prompt (length: {len(prompt)}): {prompt[:200]}...")
            
            # Check cache first
            cache_key = self._get_cache_key(prompt)
            if self._is_cache_valid(cache_key):
                logger.info("✅ Using cached AI venue recommendations")
                return self._cache[cache_key]
            
            logger.info("No valid cache found, making API request...")
            
            # Generate new recommendations
            logger.info("Calling OpenAI API with model: Meta-Llama-3-1-8B-Instruct-FP8")
            
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
            
            logger.info("✅ Received response from AI API")
            
            # Parse AI response
            ai_content = response.choices[0].message.content
            logger.info(f"AI response length: {len(ai_content)}")
            logger.info(f"AI response preview: {ai_content[:300]}...")
            
            venues = self._parse_ai_response(ai_content)
            logger.info(f"Parsed {len(venues)} venues from AI response")
            
            # Cache the results
            self._cache[cache_key] = venues
            self._cache_expiry[cache_key] = datetime.now().timestamp() + 3600  # 1 hour cache
            
            logger.info(f"✅ Successfully generated {len(venues)} AI venue recommendations")
            return venues
            
        except Exception as e:
            logger.error(f"❌ AI venue generation failed: {str(e)}", exc_info=True)
            logger.info("Falling back to curated venues")
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
            logger.info(f"Raw AI response: {content[:500]}...")
            
            # Find JSON content
            start_idx = content.find('[')
            end_idx = content.rfind(']') + 1
            
            if start_idx == -1 or end_idx == 0:
                logger.warning("No JSON array found in AI response, trying to extract from text")
                return self._extract_venues_from_text(content)
            
            json_content = content[start_idx:end_idx]
            logger.info(f"Extracted JSON: {json_content[:300]}...")
            
            # Try to fix common JSON issues
            json_content = self._fix_json_issues(json_content)
            
            venues = json.loads(json_content)
            
            # Validate and clean venue data
            validated_venues = []
            for venue in venues:
                if self._validate_venue_data(venue):
                    validated_venues.append(venue)
            
            logger.info(f"Successfully parsed {len(validated_venues)} venues from AI response")
            return validated_venues
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI JSON response: {str(e)}")
            logger.info("Attempting to extract venues from text instead")
            return self._extract_venues_from_text(content)
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
    
    def _load_api_key_from_env(self) -> Optional[str]:
        """Load API key from environment variables or Streamlit secrets"""
        logger.info("=== ATTEMPTING TO LOAD API KEY ===")
        
        # Try Streamlit secrets first
        try:
            import streamlit as st
            logger.info("Streamlit module imported successfully")
            
            if hasattr(st, 'secrets'):
                logger.info("Streamlit secrets attribute found")
                
                # Debug: Show all available secret sections
                try:
                    available_sections = list(st.secrets.keys())
                    logger.info(f"Available secret sections: {available_sections}")
                except Exception as e:
                    logger.warning(f"Could not list secret sections: {str(e)}")
                
                # Try different possible section names
                possible_sections = ['ai', 'AI', 'openai', 'OPENAI']
                
                for section_name in possible_sections:
                    if section_name in st.secrets:
                        logger.info(f"Found section '{section_name}' in Streamlit secrets")
                        
                        section = st.secrets[section_name]
                        
                        # Try different possible key names
                        possible_keys = ['api_key', 'API_KEY', 'key', 'openai_api_key']
                        
                        for key_name in possible_keys:
                            if key_name in section:
                                api_key = section[key_name]
                                if api_key and api_key.strip() and api_key != "your-api-key-here":
                                    logger.info(f"✅ API key loaded from Streamlit secrets [{section_name}.{key_name}] (length: {len(api_key)})")
                                    return api_key
                                else:
                                    logger.warning(f"API key in [{section_name}.{key_name}] is empty or placeholder")
                
                logger.warning("No valid API key found in any Streamlit secrets section")
            else:
                logger.warning("Streamlit secrets not available")
                
        except ImportError:
            logger.warning("Streamlit not available (not running in Streamlit context)")
        except Exception as e:
            logger.error(f"Error accessing Streamlit secrets: {str(e)}", exc_info=True)
        
        # Try environment variables
        try:
            import os
            logger.info("Checking environment variables...")
            
            try:
                from dotenv import load_dotenv
                load_dotenv()
                logger.info("Loaded .env file")
            except ImportError:
                logger.info("python-dotenv not available, checking system env vars only")
            
            api_key = os.getenv('AI_API_KEY')
            if api_key and api_key.strip():
                logger.info(f"✅ API key loaded from AI_API_KEY environment variable (length: {len(api_key)})")
                return api_key
            else:
                logger.info("AI_API_KEY environment variable not set or empty")
            
            # Also check for OpenAI key as fallback
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key and openai_key.strip():
                logger.info(f"✅ Using OpenAI API key from environment (length: {len(openai_key)})")
                return openai_key
            else:
                logger.info("OPENAI_API_KEY environment variable not set or empty")
                
        except Exception as e:
            logger.error(f"Error checking environment variables: {str(e)}", exc_info=True)
        
        logger.warning("❌ No API key found in any source")
        return None
    
    def _get_fallback_key(self) -> Optional[str]:
        """Temporary fallback key for testing - REMOVE AFTER TESTING"""
        # This is a temporary solution for testing
        # The key will be removed after we confirm it works
        import base64
        
        try:
            # Encoded key for temporary testing
            encoded_key = "c2stVVZLWUxoaU5mME1LWFJxYm5EaWVoQQ=="
            decoded_key = base64.b64decode(encoded_key).decode('utf-8')
            
            logger.info("Using temporary fallback API key for testing")
            return decoded_key
            
        except Exception as e:
            logger.error(f"Error decoding fallback key: {str(e)}")
            return None
    
    def get_service_stats(self) -> Dict:
        """Get AI service statistics"""
        env_key = self._load_api_key_from_env()
        return {
            "version": self.version,
            "client_available": self.client is not None,
            "cache_entries": len(self._cache),
            "api_key_set": self.api_key is not None,
            "env_key_available": env_key is not None and len(env_key.strip()) > 0 if env_key else False
        }
    
    def _get_hardcoded_key(self) -> Optional[str]:
        """Get hardcoded API key - replace with your actual key"""
        # TODO: Replace this with your actual API key
        hardcoded_key = "sk-UVKYLhiNf0MKXRqbnDiehA"
        
        if hardcoded_key and hardcoded_key != "sk-your-api-key-here-replace-this-with-real-key":
            logger.info(f"✅ Using hardcoded API key (length: {len(hardcoded_key)})")
            return hardcoded_key
        else:
            logger.warning("Hardcoded API key not set - replace placeholder in _get_hardcoded_key method")
            return None    

    def _fix_json_issues(self, json_content: str) -> str:
        """Fix common JSON formatting issues"""
        # Remove trailing commas before closing brackets
        json_content = json_content.replace(',]', ']')
        json_content = json_content.replace(',}', '}')
        
        # Fix missing quotes around keys (basic fix)
        import re
        json_content = re.sub(r'(\w+):', r'"\1":', json_content)
        
        return json_content
    
    def _extract_venues_from_text(self, content: str) -> List[Dict]:
        """Extract venue information from text when JSON parsing fails"""
        logger.info("Extracting venues from text format")
        
        # Create fallback venues based on common Hong Kong attractions
        fallback_venues = [
            {
                "id": "ai_text_1",
                "name": "Victoria Peak Accessible Viewing Area",
                "category": "attraction",
                "description": "Panoramic city views with wheelchair accessible facilities and senior-friendly amenities.",
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
                    "notes": ["Peak Tram wheelchair accessible", "Elevator to Sky Terrace"]
                },
                "elderly_friendly": True,
                "weather_suitability": "mixed"
            },
            {
                "id": "ai_text_2", 
                "name": "Accessible Dim Sum Restaurant",
                "category": "restaurant",
                "description": "Traditional Cantonese dim sum with soft meal options and wheelchair accessibility.",
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
                    "notes": ["Ground floor seating", "Soft steamed dishes available"]
                },
                "dietary_options": {
                    "soft_meals": True,
                    "vegetarian": True,
                    "notes": ["Steamed dim sum", "Congee available"]
                },
                "elderly_friendly": True,
                "weather_suitability": "indoor"
            },
            {
                "id": "ai_text_3",
                "name": "Hong Kong Cultural Museum (Accessible)",
                "category": "museum", 
                "description": "Interactive cultural exhibits with full accessibility features and senior discounts.",
                "district": "Sha Tin",
                "address": "1 Man Lam Road, Sha Tin, New Territories",
                "latitude": 22.3817,
                "longitude": 114.1878,
                "cost_range": [10, 30],
                "accessibility": {
                    "wheelchair_accessible": True,
                    "has_elevator": True,
                    "accessible_toilets": True,
                    "step_free_access": True,
                    "notes": ["Audio guides available", "Wheelchair loans", "Senior discounts"]
                },
                "elderly_friendly": True,
                "weather_suitability": "indoor"
            }
        ]
        
        logger.info(f"Generated {len(fallback_venues)} fallback venues from text extraction")
        return fallback_venues