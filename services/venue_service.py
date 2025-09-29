"""
Venue Service for Hong Kong Trip Planner
Handles venue database operations and accessibility filtering
"""

from typing import List, Optional
import sqlite3
import logging
from models import Venue, VenueCategory, Location, AccessibilityInfo, DietaryOption, WeatherSuitability, SearchCriteria
from database import get_db_connection
import json

# Configure logging
logger = logging.getLogger(__name__)

class VenueService:
    """Service for managing venue data and searches"""
    
    def __init__(self):
        """Initialize venue service"""
        pass
    
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
        """Get all venues from database"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM venues")
            rows = cursor.fetchall()
            
            return [self._row_to_venue(row) for row in rows]
    
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