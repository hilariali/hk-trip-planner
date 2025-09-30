"""
Venue Service for Hong Kong Trip Planner
Handles venue database operations and accessibility filtering
"""

from typing import List, Optional
import sqlite3
import logging
from models import Venue, VenueCategory, Location, AccessibilityInfo, DietaryOption, WeatherSuitability, SearchCriteria
from database import get_db_connection
from services.offline_data_service import OfflineDataService
# Lazy imports to avoid circular dependencies
import json

# Configure logging
logger = logging.getLogger('services.venue_service')

class VenueService:
    """Service for managing venue data and searches"""
    
    def __init__(self):
        """Initialize venue service"""
        self._hk_gov_service = None
        self._facilities_service = None
        self._offline_service = None
        self._ai_service = None
        self._gov_data_cache = None
        self._ai_data_cache = None
        self._last_update = None
    
    def _get_hk_gov_service(self):
        """Get HK government service with safe import"""
        if self._hk_gov_service is None:
            try:
                from .hk_gov_data_service import HKGovDataService
                self._hk_gov_service = HKGovDataService()
            except ImportError as e:
                logger.warning(f"Could not import HK government service: {e}")
                self._hk_gov_service = None
        return self._hk_gov_service
    
    def _get_offline_service(self):
        """Get offline data service with safe import"""
        if self._offline_service is None:
            try:
                from .offline_data_service import OfflineDataService
                self._offline_service = OfflineDataService()
                logger.info("Offline data service initialized successfully")
            except ImportError as e:
                logger.warning(f"Could not import offline data service: {e}")
                self._offline_service = None
        return self._offline_service
    
    def _get_ai_service(self):
        """Get AI venue service with safe import"""
        if self._ai_service is None:
            try:
                from .ai_venue_service import AIVenueService
                self._ai_service = AIVenueService()
                logger.info("AI venue service initialized successfully")
            except ImportError as e:
                logger.warning(f"Could not import AI venue service: {e}")
                self._ai_service = None
        return self._ai_service
    
    def set_ai_api_key(self, api_key: str):
        """Set API key for AI venue service"""
        ai_service = self._get_ai_service()
        if ai_service:
            ai_service.set_api_key(api_key)
            logger.info("AI API key configured successfully")
        else:
            logger.warning("AI service not available for API key configuration")
    
    def _get_facilities_service(self):
        """Get facilities service with safe import"""
        if self._facilities_service is None:
            try:
                from .facilities_service import FacilitiesService
                self._facilities_service = FacilitiesService()
            except ImportError as e:
                logger.warning(f"Could not import facilities service: {e}")
                self._facilities_service = None
        return self._facilities_service
    
    def search_venues(self, criteria: SearchCriteria) -> List[Venue]:
        """Search venues based on criteria"""
        logger.info(f"Searching venues with criteria: {len(criteria.accessibility_required)} accessibility, {len(criteria.dietary_required)} dietary")
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Build dynamic query based on criteria
            query = "SELECT * FROM venues WHERE 1=1"
            params = []
            
            if criteria.categories:
                category_placeholders = ','.join(['?' for _ in criteria.categories])
                query += f" AND category IN ({category_placeholders})"
                params.extend([cat.value for cat in criteria.categories])
            
            if criteria.max_cost:
                query += " AND cost_min <= ?"
                params.append(criteria.max_cost)
            
            if criteria.accessibility_required:
                if 'wheelchair' in criteria.accessibility_required:
                    query += " AND wheelchair_accessible = 1"
                if 'elevator_only' in criteria.accessibility_required:
                    query += " AND has_elevator = 1"
                if 'avoid_stairs' in criteria.accessibility_required:
                    query += " AND step_free_access = 1"
            
            if criteria.dietary_required:
                # Only apply dietary filters to restaurants
                dietary_conditions = []
                if 'soft_meals' in criteria.dietary_required:
                    dietary_conditions.append("soft_meals_available = 1")
                if 'vegetarian' in criteria.dietary_required:
                    dietary_conditions.append("vegetarian_options = 1")
                if 'halal' in criteria.dietary_required:
                    dietary_conditions.append("halal_options = 1")
                
                if dietary_conditions:
                    dietary_filter = " OR ".join(dietary_conditions)
                    query += f" AND (category != 'restaurant' OR ({dietary_filter}))"
            
            if criteria.weather_suitability:
                query += " AND weather_suitability = ?"
                params.append(criteria.weather_suitability.value)
            
            if criteria.district:
                query += " AND district = ?"
                params.append(criteria.district)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            venues = [self._row_to_venue(row) for row in rows]
            logger.info(f"Found {len(venues)} matching venues")
            
            return venues
    
    def get_venue_by_id(self, venue_id: str) -> Optional[Venue]:
        """Get a specific venue by ID"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM venues WHERE id = ?", (venue_id,))
            row = cursor.fetchone()
            
            if row:
                return self._row_to_venue(row)
            return None
    
    def get_all_venues(self) -> List[Venue]:
        """Get all venues from offline data, database, government APIs, and AI"""
        try:
            # Start with reliable offline data as foundation
            offline_venues = self._get_offline_venues()
            
            # Add venues from local database
            local_venues = []
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM venues")
                rows = cursor.fetchall()
                local_venues = [self._row_to_venue(row) for row in rows]
            
            # Enhance with government APIs (optional)
            gov_venues = self._get_government_venues()
            
            # Add AI-generated venues (optional)
            ai_venues = self._get_ai_venues()
            
            # Combine all sources
            all_venues = offline_venues + local_venues + gov_venues + ai_venues
            logger.info(f"Retrieved {len(offline_venues)} offline + {len(local_venues)} local + {len(gov_venues)} government + {len(ai_venues)} AI venues = {len(all_venues)} total")
            
            return all_venues
            
        except Exception as e:
            logger.error(f"Error getting venues: {str(e)}")
            # Always return at least offline venues as reliable fallback
            return self._get_offline_venues()
    
    def get_ai_enhanced_venues(self, preferences: dict, weather_data: dict = None) -> List[Venue]:
        """Get AI-generated venues based on user preferences"""
        logger.info("=== GETTING AI-ENHANCED VENUES ===")
        logger.info(f"Preferences: {preferences}")
        logger.info(f"Weather data: {weather_data}")
        
        try:
            ai_service = self._get_ai_service()
            if not ai_service:
                logger.warning("AI service not available - using standard venues")
                return self.get_all_venues()
            
            logger.info("✅ AI service available, generating venues...")
            
            # Generate AI venues based on preferences
            ai_venue_data = ai_service.generate_venues_for_preferences(preferences, weather_data)
            logger.info(f"Received {len(ai_venue_data)} AI venue data items")
            
            # Convert to Venue objects
            ai_venues = []
            for i, venue_data in enumerate(ai_venue_data):
                logger.info(f"Converting AI venue {i+1}: {venue_data.get('name', 'Unknown')}")
                venue = self._convert_ai_data_to_venue(venue_data)
                if venue:
                    ai_venues.append(venue)
                    logger.info(f"✅ Successfully converted venue: {venue.name}")
                else:
                    logger.warning(f"❌ Failed to convert venue data: {venue_data}")
            
            # Combine with offline venues for reliability
            offline_venues = self._get_offline_venues()
            
            all_venues = offline_venues + ai_venues
            logger.info(f"✅ Final result: {len(ai_venues)} AI venues + {len(offline_venues)} offline venues = {len(all_venues)} total")
            
            return all_venues
            
        except Exception as e:
            logger.error(f"❌ Error getting AI-enhanced venues: {str(e)}", exc_info=True)
            logger.info("Falling back to standard venues")
            return self.get_all_venues()
    
    def get_venues_by_category(self, category: VenueCategory) -> List[Venue]:
        """Get venues by category"""
        criteria = SearchCriteria(categories=[category])
        return self.search_venues(criteria)
    
    def get_accessible_venues(self, accessibility_needs: List[str]) -> List[Venue]:
        """Get venues that meet accessibility requirements"""
        criteria = SearchCriteria(accessibility_required=accessibility_needs)
        return self.search_venues(criteria)
    
    def get_dietary_friendly_venues(self, dietary_restrictions: List[str]) -> List[Venue]:
        """Get venues that accommodate dietary restrictions"""
        criteria = SearchCriteria(dietary_required=dietary_restrictions)
        return self.search_venues(criteria)
    
    def _row_to_venue(self, row) -> Venue:
        """Convert database row to Venue object"""
        # Parse opening hours JSON
        opening_hours = {}
        if row['opening_hours']:
            try:
                opening_hours = json.loads(row['opening_hours'])
            except json.JSONDecodeError:
                opening_hours = {}
        
        # Create location
        location = Location(
            latitude=row['latitude'] or 0.0,
            longitude=row['longitude'] or 0.0,
            address=row['address'] or "",
            district=row['district'] or ""
        )
        
        # Create accessibility info
        accessibility_notes = []
        if row['accessibility_notes']:
            accessibility_notes = row['accessibility_notes'].split(';')
        
        accessibility = AccessibilityInfo(
            has_elevator=bool(row['has_elevator']),
            wheelchair_accessible=bool(row['wheelchair_accessible']),
            accessible_toilets=bool(row['accessible_toilets']),
            step_free_access=bool(row['step_free_access']),
            parent_facilities=bool(row['parent_facilities']),
            rest_areas=bool(row['rest_areas']),
            difficulty_level=row['difficulty_level'] or 1,
            accessibility_notes=accessibility_notes
        )
        
        # Create dietary options
        dietary_notes = []
        if row['dietary_notes']:
            dietary_notes = row['dietary_notes'].split(';')
        
        dietary_options = DietaryOption(
            soft_meals=bool(row['soft_meals_available']),
            vegetarian=bool(row['vegetarian_options']),
            halal=bool(row['halal_options']),
            no_seafood=bool(row['no_seafood_options']),
            allergy_friendly=bool(row['allergy_friendly']),
            dietary_notes=dietary_notes
        )
        
        # Determine weather suitability
        weather_suitability = WeatherSuitability.MIXED
        if row['weather_suitability']:
            try:
                weather_suitability = WeatherSuitability(row['weather_suitability'])
            except ValueError:
                weather_suitability = WeatherSuitability.MIXED
        
        return Venue(
            id=row['id'],
            name=row['name'],
            category=VenueCategory(row['category']),
            location=location,
            accessibility=accessibility,
            dietary_options=dietary_options,
            cost_range=(row['cost_min'] or 0, row['cost_max'] or 0),
            opening_hours=opening_hours,
            weather_suitability=weather_suitability,
            description=row['description'] or "",
            phone=row['phone'] or "",
            website=row['website'] or "",
            elderly_discount=bool(row['elderly_discount']),
            child_discount=bool(row['child_discount'])
        )
    
    def _get_government_venues(self) -> List[Venue]:
        """Get venues from Hong Kong government APIs"""
        try:
            from datetime import datetime, timedelta
            
            # Check if we need to refresh cache (refresh every 6 hours to reduce API calls)
            now = datetime.now()
            if (self._gov_data_cache is None or 
                self._last_update is None or 
                now - self._last_update > timedelta(hours=6)):
                
                logger.info("Refreshing government venue data...")
                self._refresh_government_data()
                self._last_update = now
            
            return self._gov_data_cache or []
            
        except Exception as e:
            logger.warning(f"Error fetching government venues: {str(e)}")
            return []
    
    def _refresh_government_data(self):
        """Refresh government venue data from APIs"""
        try:
            gov_venues = []
            
            hk_gov_service = self._get_hk_gov_service()
            if hk_gov_service:
                # Get major attractions (limit API calls)
                attractions = hk_gov_service.get_major_attractions()
                for attraction_data in attractions[:10]:  # Reduced limit
                    venue = hk_gov_service.convert_to_venue(attraction_data)
                    if venue:
                        gov_venues.append(venue)
                
                # Only try events and facilities if attractions worked
                if attractions:
                    # Get HKTB events (as temporary attractions)
                    events = hk_gov_service.get_hktb_events()
                    for event_data in events[:5]:  # Reduced limit
                        venue = hk_gov_service.convert_to_venue(event_data)
                        if venue:
                            gov_venues.append(venue)
                    
                    # Get accessible facilities
                    facilities = hk_gov_service.get_accessible_facilities()
                    for facility_data in facilities[:5]:  # Reduced limit
                        venue = hk_gov_service.convert_to_venue(facility_data)
                        if venue:
                            gov_venues.append(venue)
            
            self._gov_data_cache = gov_venues
            if gov_venues:
                logger.info(f"Cached {len(gov_venues)} government venues")
            else:
                logger.info("No government venues available - using local database only")
            
        except Exception as e:
            logger.warning(f"Error refreshing government data: {str(e)}")
            self._gov_data_cache = []
    
    def get_nearby_facilities(self, latitude: float, longitude: float, radius_km: float = 1.0):
        """Get nearby public facilities like toilets and accessibility services"""
        try:
            facilities_service = self._get_facilities_service()
            if facilities_service:
                return facilities_service.get_nearby_facilities(latitude, longitude, radius_km)
            return []
        except Exception as e:
            logger.warning(f"Error getting nearby facilities: {str(e)}")
            return []
    
    def get_mtr_accessibility_info(self):
        """Get MTR accessibility information"""
        try:
            hk_gov_service = self._get_hk_gov_service()
            if hk_gov_service:
                return hk_gov_service.get_mtr_accessibility_info()
            return {}
        except Exception as e:
            logger.warning(f"Error getting MTR accessibility info: {str(e)}")
            return {} 
   
    def _get_offline_venues(self) -> List[Venue]:
        """Get venues from offline data service"""
        try:
            offline_service = self._get_offline_service()
            if offline_service:
                offline_venues = offline_service.get_all_venues()
                logger.info(f"Loaded {len(offline_venues)} offline venues")
                return offline_venues
            else:
                logger.warning("Offline service not available")
                return []
            
        except Exception as e:
            logger.warning(f"Error loading offline venues: {str(e)}")
            return []
    
    def _get_offline_service(self) -> Optional[OfflineDataService]:
        """Get offline data service instance"""
        if self._offline_service is None:
            try:
                self._offline_service = OfflineDataService()
            except Exception as e:
                logger.warning(f"Could not initialize offline data service: {str(e)}")
                return None
        return self._offline_service
    
    def _get_ai_venues(self) -> List[Venue]:
        """Get AI-generated venues"""
        try:
            ai_service = self._get_ai_service()
            if not ai_service:
                return []
            
            # Use cached AI venues if available
            if self._ai_data_cache:
                logger.info("Using cached AI venues")
                return self._ai_data_cache
            
            # Generate basic AI venues (no specific preferences)
            basic_preferences = {
                'family_composition': {'adults': 2, 'children': 0, 'seniors': 1},
                'mobility_needs': ['wheelchair'],
                'dietary_restrictions': ['soft_meals'],
                'budget_range': (200, 800),
                'trip_duration': 3
            }
            
            ai_venue_data = ai_service.generate_venues_for_preferences(basic_preferences)
            
            # Convert to Venue objects
            ai_venues = []
            for venue_data in ai_venue_data:
                venue = self._convert_ai_data_to_venue(venue_data)
                if venue:
                    ai_venues.append(venue)
            
            # Cache the results
            self._ai_data_cache = ai_venues
            logger.info(f"Generated and cached {len(ai_venues)} AI venues")
            
            return ai_venues
            
        except Exception as e:
            logger.warning(f"Error generating AI venues: {str(e)}")
            return []
    
    def _convert_ai_data_to_venue(self, ai_data: dict) -> Optional[Venue]:
        """Convert AI-generated data to Venue object"""
        try:
            # Create location
            location = Location(
                latitude=ai_data.get('latitude', 22.3),
                longitude=ai_data.get('longitude', 114.2),
                address=ai_data.get('address', ''),
                district=ai_data.get('district', '')
            )
            
            # Create accessibility info
            accessibility_data = ai_data.get('accessibility', {})
            accessibility = AccessibilityInfo(
                has_elevator=accessibility_data.get('has_elevator', False),
                wheelchair_accessible=accessibility_data.get('wheelchair_accessible', False),
                accessible_toilets=accessibility_data.get('accessible_toilets', False),
                step_free_access=accessibility_data.get('step_free_access', False),
                parent_facilities=False,
                rest_areas=True,
                difficulty_level=1 if accessibility_data.get('wheelchair_accessible') else 2,
                accessibility_notes=accessibility_data.get('notes', [])
            )
            
            # Create dietary options
            dietary_data = ai_data.get('dietary_options', {})
            dietary_options = DietaryOption(
                soft_meals=dietary_data.get('soft_meals', False),
                vegetarian=dietary_data.get('vegetarian', False),
                halal=dietary_data.get('halal', False),
                no_seafood=dietary_data.get('no_seafood', False),
                allergy_friendly=False,
                dietary_notes=dietary_data.get('notes', [])
            )
            
            # Map category
            category_mapping = {
                'attraction': VenueCategory.ATTRACTION,
                'restaurant': VenueCategory.RESTAURANT,
                'transport': VenueCategory.TRANSPORT,
                'shopping': VenueCategory.SHOPPING,
                'park': VenueCategory.PARK,
                'museum': VenueCategory.MUSEUM
            }
            
            category = category_mapping.get(ai_data.get('category', 'attraction'), VenueCategory.ATTRACTION)
            
            # Map weather suitability
            weather_map = {
                'indoor': WeatherSuitability.INDOOR,
                'outdoor': WeatherSuitability.OUTDOOR,
                'mixed': WeatherSuitability.MIXED
            }
            
            weather_suitability = weather_map.get(
                ai_data.get('weather_suitability', 'mixed'), 
                WeatherSuitability.MIXED
            )
            
            # Get cost range
            cost_range = ai_data.get('cost_range', [0, 100])
            if not isinstance(cost_range, (list, tuple)) or len(cost_range) != 2:
                cost_range = [0, 100]
            
            return Venue(
                id=ai_data.get('id', f"ai_{hash(ai_data.get('name', 'unknown'))}"),
                name=ai_data.get('name', 'AI Generated Venue'),
                category=category,
                location=location,
                accessibility=accessibility,
                dietary_options=dietary_options,
                cost_range=tuple(cost_range),
                opening_hours=ai_data.get('opening_hours', {}),
                weather_suitability=weather_suitability,
                description=ai_data.get('description', ''),
                phone=ai_data.get('phone', ''),
                website=ai_data.get('website', ''),
                elderly_discount=ai_data.get('elderly_friendly', False),
                child_discount=False
            )
            
        except Exception as e:
            logger.warning(f"Error converting AI venue data: {str(e)}")
            return None