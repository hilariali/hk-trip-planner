#!/usr/bin/env python3
"""
Simple test to verify all imports work correctly
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test all service imports"""
    print("Testing imports...")
    
    try:
        print("✓ Testing models import...")
        from models import Venue, UserPreferences, Itinerary
        
        print("✓ Testing database import...")
        from database import init_database, get_venue_count
        
        print("✓ Testing weather service import...")
        from services.weather_service import WeatherService
        
        print("✓ Testing venue service import...")
        from services.venue_service import VenueService
        
        print("✓ Testing itinerary engine import...")
        from services.itinerary_engine import ItineraryEngine
        
        print("✓ Testing HK gov data service import...")
        from services.hk_gov_data_service import HKGovDataService
        
        print("✓ Testing facilities service import...")
        from services.facilities_service import FacilitiesService
        
        print("✅ All imports successful!")
        
        # Test basic initialization
        print("\nTesting service initialization...")
        weather_service = WeatherService()
        print("✓ Weather service initialized")
        
        venue_service = VenueService()
        print("✓ Venue service initialized")
        
        itinerary_engine = ItineraryEngine()
        print("✓ Itinerary engine initialized")
        
        print("✅ All services initialized successfully!")
        
    except Exception as e:
        print(f"❌ Import test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)