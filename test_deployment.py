#!/usr/bin/env python3
"""
Test script to verify deployment readiness
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    try:
        print("Testing imports...")
        import streamlit as st
        print("✅ Streamlit imported")
        
        import pandas as pd
        print("✅ Pandas imported")
        
        import sqlite3
        print("✅ SQLite3 imported")
        
        from models import Venue, UserPreferences, Itinerary
        print("✅ Models imported")
        
        from services.venue_service import VenueService
        print("✅ VenueService imported")
        
        from services.weather_service import WeatherService
        print("✅ WeatherService imported")
        
        from services.itinerary_engine import ItineraryEngine
        print("✅ ItineraryEngine imported")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_database():
    """Test database initialization"""
    try:
        print("Testing database...")
        import database
        database.init_database()
        database.seed_sample_data()
        count = database.get_venue_count()
        print(f"✅ Database initialized with {count} venues")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_services():
    """Test service initialization"""
    try:
        print("Testing services...")
        from services.venue_service import VenueService
        from services.weather_service import WeatherService
        from services.itinerary_engine import ItineraryEngine
        
        venue_service = VenueService()
        weather_service = WeatherService()
        itinerary_engine = ItineraryEngine()
        
        venues = venue_service.get_all_venues()
        print(f"✅ VenueService working - {len(venues)} venues loaded")
        
        weather = weather_service.get_current_weather()
        print(f"✅ WeatherService working - {weather.temperature}°C")
        
        print("✅ All services initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Service error: {e}")
        return False

def main():
    print("🏙️ SilverJoy Planner HK - Deployment Test")
    print("=" * 50)
    
    success = True
    
    if not test_imports():
        success = False
    
    if not test_database():
        success = False
    
    if not test_services():
        success = False
    
    if success:
        print("\n🎉 All tests passed! Ready for deployment.")
        print("\n📋 Deployment steps:")
        print("1. Code is already pushed to GitHub ✅")
        print("2. Go to https://share.streamlit.io")
        print("3. Sign in with GitHub")
        print("4. Click 'New app'")
        print("5. Select repository: hk-trip-planner")
        print("6. Main file: app.py")
        print("7. Click 'Deploy!'")
        print("\n🔐 Don't forget to add secrets in Streamlit Cloud:")
        print("[ai]")
        print("api_key = \"sk-UVKYLhiNf0MKXRqbnDiehA\"")
        print("base_url = \"https://chatapi.akash.network/api/v1\"")
        print("model = \"Meta-Llama-3-1-8B-Instruct-FP8\"")
    else:
        print("\n❌ Some tests failed. Please fix issues before deployment.")
        sys.exit(1)

if __name__ == "__main__":
    main()