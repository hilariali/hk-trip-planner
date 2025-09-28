"""
Test script for Hong Kong Trip Planner components
"""

from models import UserPreferences, VenueCategory, SearchCriteria
from services.venue_service import VenueService
from services.weather_service import WeatherService
from services.itinerary_engine import ItineraryEngine
from database import init_database, seed_sample_data, get_venue_count

def test_database():
    """Test database functionality"""
    print("Testing database...")
    
    # Initialize database
    init_database()
    seed_sample_data()
    
    count = get_venue_count()
    print(f"✅ Database initialized with {count} venues")

def test_venue_service():
    """Test venue service"""
    print("\nTesting venue service...")
    
    venue_service = VenueService()
    
    # Test getting all venues
    all_venues = venue_service.get_all_venues()
    print(f"✅ Found {len(all_venues)} total venues")
    
    # Test category filtering
    restaurants = venue_service.get_venues_by_category(VenueCategory.RESTAURANT)
    print(f"✅ Found {len(restaurants)} restaurants")
    
    # Test accessibility filtering
    accessible_venues = venue_service.get_accessible_venues(['wheelchair'])
    print(f"✅ Found {len(accessible_venues)} wheelchair accessible venues")
    
    # Test specific venue
    venue = venue_service.get_venue_by_id('hk_001')
    if venue:
        print(f"✅ Retrieved venue: {venue.name}")
    else:
        print("❌ Could not retrieve specific venue")

def test_weather_service():
    """Test weather service"""
    print("\nTesting weather service...")
    
    weather_service = WeatherService()
    
    # Test current weather (will use mock data)
    current_weather = weather_service.get_current_weather()
    print(f"✅ Current weather: {current_weather.temperature}°C, {current_weather.weather_description}")
    
    # Test forecast
    forecast = weather_service.get_forecast(3)
    print(f"✅ 3-day forecast retrieved with {len(forecast)} days")

def test_itinerary_engine():
    """Test itinerary generation"""
    print("\nTesting itinerary engine...")
    
    # Create sample preferences
    preferences = UserPreferences(
        family_composition={'adults': 2, 'seniors': 1, 'children': 0},
        mobility_needs=['wheelchair', 'elevator_only'],
        dietary_restrictions=['soft_meals'],
        budget_range=(200, 600),
        trip_duration=2,
        transportation_preference=['mtr', 'taxi']
    )
    
    weather_service = WeatherService()
    weather_data = weather_service.get_current_weather()
    
    itinerary_engine = ItineraryEngine()
    
    try:
        itinerary = itinerary_engine.generate_itinerary(preferences, weather_data)
        print(f"✅ Generated {len(itinerary.day_plans)}-day itinerary")
        print(f"   Total cost: HKD {itinerary.total_cost:.0f}")
        print(f"   Accessibility score: {itinerary.accessibility_score}/5")
        
        for day_plan in itinerary.day_plans:
            print(f"   Day {day_plan.day}: {len(day_plan.venues)} venues, HKD {day_plan.estimated_cost:.0f}")
            
    except Exception as e:
        print(f"❌ Error generating itinerary: {str(e)}")

def main():
    """Run all tests"""
    print("🏙️ Hong Kong Trip Planner - Component Tests\n")
    
    test_database()
    test_venue_service()
    test_weather_service()
    test_itinerary_engine()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()