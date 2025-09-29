#!/usr/bin/env python3
"""
Debug test script to check itinerary generation
"""

import logging
from models import UserPreferences
from services.venue_service import VenueService
from services.weather_service import WeatherService
from services.itinerary_engine import ItineraryEngine
from database import init_database, seed_sample_data, get_venue_count

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_itinerary_generation():
    """Test the itinerary generation process"""
    logger.info("=== STARTING DEBUG TEST ===")
    
    # Initialize database
    logger.info("Initializing database...")
    init_database()
    seed_sample_data()
    logger.info(f"Database has {get_venue_count()} venues")
    
    # Create test preferences
    logger.info("Creating test user preferences...")
    preferences = UserPreferences(
        family_composition={"adults": 2, "children": 0, "seniors": 1},
        mobility_needs=["wheelchair", "elevator_only"],
        dietary_restrictions=["soft_meals"],
        budget_range=(300, 800),
        trip_duration=2,
        transportation_preference=["mtr", "taxi"]
    )
    logger.info(f"Test preferences: {preferences}")
    
    # Initialize services
    logger.info("Initializing services...")
    venue_service = VenueService()
    weather_service = WeatherService()
    itinerary_engine = ItineraryEngine()
    
    # Test venue service
    logger.info("Testing venue service...")
    all_venues = venue_service.get_all_venues()
    logger.info(f"Found {len(all_venues)} total venues")
    for venue in all_venues:
        logger.info(f"  - {venue.name} ({venue.category.value})")
    
    # Test weather service
    logger.info("Testing weather service...")
    weather = weather_service.get_current_weather()
    logger.info(f"Weather: {weather}")
    
    # Test itinerary generation
    logger.info("Testing itinerary generation...")
    try:
        itinerary = itinerary_engine.generate_itinerary(preferences, weather)
        logger.info(f"SUCCESS: Generated itinerary with {len(itinerary.day_plans)} days")
        logger.info(f"Total cost: {itinerary.total_cost}")
        logger.info(f"Accessibility score: {itinerary.accessibility_score}")
        
        for day_plan in itinerary.day_plans:
            logger.info(f"Day {day_plan.day}: {len(day_plan.venues)} venues")
            for venue in day_plan.venues:
                logger.info(f"  - {venue.name}")
                
    except Exception as e:
        logger.error(f"FAILED: {str(e)}", exc_info=True)

if __name__ == "__main__":
    test_itinerary_generation()