"""
Offline Data Service for Hong Kong Trip Planner
Provides reliable venue data without depending on external APIs
"""

import logging
from typing import List, Optional
from models import Venue, VenueCategory, Location, AccessibilityInfo, DietaryOption, WeatherSuitability
from data.hk_attractions_offline import get_all_offline_venues, get_venues_by_category, get_accessible_venues

# Configure logging
logger = logging.getLogger('services.offline_data_service')

class OfflineDataService:
    """Service for managing offline venue data"""
    
    def __init__(self):
        """Initialize offline data service"""
        self.version = "2025-09-29-offline-v1"
        logger.info(f"OfflineDataService initialized - Version: {self.version}")
    
    def get_all_venues(self) -> List[Venue]:
        """Get all offline venues as Venue objects"""
        offline_data = get_all_offline_venues()
        venues = []
        
        for venue_data in offline_data:
            venue = self._convert_to_venue(venue_data)
            if venue:
                venues.append(venue)
        
        logger.info(f"Loaded {len(venues)} offline venues")
        return venues
    
    def get_venues_by_category(self, category: VenueCategory) -> List[Venue]:
        """Get venues filtered by category"""
        category_map = {
            VenueCategory.ATTRACTION: 'attraction',
            VenueCategory.RESTAURANT: 'restaurant',
            VenueCategory.TRANSPORT: 'transport',
            VenueCategory.SHOPPING: 'shopping',
            VenueCategory.PARK: 'park',
            VenueCategory.MUSEUM: 'museum'
        }
        
        category_str = category_map.get(category, 'attraction')
        offline_data = get_venues_by_category(category_str)
        
        venues = []
        for venue_data in offline_data:
            venue = self._convert_to_venue(venue_data)
            if venue:
                venues.append(venue)
        
        return venues
    
    def get_accessible_venues(self) -> List[Venue]:
        """Get wheelchair accessible venues"""
        offline_data = get_accessible_venues()
        venues = []
        
        for venue_data in offline_data:
            venue = self._convert_to_venue(venue_data)
            if venue:
                venues.append(venue)
        
        return venues
    
    def search_venues(self, query: str) -> List[Venue]:
        """Search venues by name or description"""
        all_venues = self.get_all_venues()
        query_lower = query.lower()
        
        matching_venues = []
        for venue in all_venues:
            if (query_lower in venue.name.lower() or 
                query_lower in venue.description.lower() or
                query_lower in venue.location.district.lower()):
                matching_venues.append(venue)
        
        return matching_venues
    
    def _convert_to_venue(self, venue_data: dict) -> Optional[Venue]:
        """Convert offline venue data to Venue object"""
        try:
            # Create location
            location = Location(
                latitude=venue_data.get('latitude', 0.0),
                longitude=venue_data.get('longitude', 0.0),
                address=venue_data.get('address', ''),
                district=venue_data.get('district', '')
            )
            
            # Create accessibility info
            accessibility_data = venue_data.get('accessibility', {})
            accessibility = AccessibilityInfo(
                has_elevator=accessibility_data.get('has_elevator', False),
                wheelchair_accessible=accessibility_data.get('wheelchair_accessible', False),
                accessible_toilets=accessibility_data.get('accessible_toilets', False),
                step_free_access=accessibility_data.get('step_free_access', False),
                parent_facilities=False,  # Not specified in offline data
                rest_areas=True,  # Assume available for elderly-friendly venues
                difficulty_level=1 if accessibility_data.get('wheelchair_accessible') else 2,
                accessibility_notes=accessibility_data.get('notes', [])
            )
            
            # Create dietary options
            dietary_data = venue_data.get('dietary_options', {})
            dietary_options = DietaryOption(
                soft_meals=dietary_data.get('soft_meals', False),
                vegetarian=dietary_data.get('vegetarian', False),
                halal=dietary_data.get('halal', False),
                no_seafood=dietary_data.get('no_seafood', False),
                allergy_friendly=False,  # Not specified
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
            
            category = category_mapping.get(venue_data.get('category', 'attraction'), VenueCategory.ATTRACTION)
            
            # Map weather suitability
            weather_map = {
                'indoor': WeatherSuitability.INDOOR,
                'outdoor': WeatherSuitability.OUTDOOR,
                'indoor_outdoor': WeatherSuitability.MIXED
            }
            
            weather_suitability = weather_map.get(
                venue_data.get('weather_suitability', 'mixed'), 
                WeatherSuitability.MIXED
            )
            
            return Venue(
                id=venue_data.get('id', ''),
                name=venue_data.get('name', ''),
                category=category,
                location=location,
                accessibility=accessibility,
                dietary_options=dietary_options,
                cost_range=tuple(venue_data.get('cost_range', (0, 100))),
                opening_hours=venue_data.get('opening_hours', {}),
                weather_suitability=weather_suitability,
                description=venue_data.get('description', ''),
                phone=venue_data.get('phone', ''),
                website=venue_data.get('website', ''),
                elderly_discount=venue_data.get('elderly_friendly', False),
                child_discount=venue_data.get('child_friendly', False)
            )
            
        except Exception as e:
            logger.warning(f"Error converting offline venue data: {str(e)}")
            return None
    
    def get_venue_stats(self) -> dict:
        """Get statistics about offline venues"""
        all_venues = self.get_all_venues()
        
        stats = {
            'total_venues': len(all_venues),
            'by_category': {},
            'accessible_count': 0,
            'elderly_friendly_count': 0,
            'free_venues_count': 0,
            'districts': set()
        }
        
        for venue in all_venues:
            # Count by category
            category_name = venue.category.value
            stats['by_category'][category_name] = stats['by_category'].get(category_name, 0) + 1
            
            # Count accessibility features
            if venue.accessibility.wheelchair_accessible:
                stats['accessible_count'] += 1
            
            if venue.elderly_discount:
                stats['elderly_friendly_count'] += 1
            
            if venue.cost_range[0] == 0:
                stats['free_venues_count'] += 1
            
            # Collect districts
            if venue.location.district:
                stats['districts'].add(venue.location.district)
        
        stats['districts'] = list(stats['districts'])
        return stats