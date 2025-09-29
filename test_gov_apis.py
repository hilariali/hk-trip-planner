#!/usr/bin/env python3
"""
Test script for Hong Kong Government API integration
"""

import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.hk_gov_data_service import HKGovDataService
from services.facilities_service import FacilitiesService
from services.weather_service import WeatherService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_government_apis():
    """Test all government API integrations"""
    logger.info("=== TESTING HONG KONG GOVERNMENT API INTEGRATION ===")
    
    # Test HK Government Data Service
    logger.info("Testing HK Government Data Service...")
    hk_gov_service = HKGovDataService()
    
    try:
        # Test attractions
        logger.info("Testing major attractions API...")
        attractions = hk_gov_service.get_major_attractions()
        logger.info(f"✅ Retrieved {len(attractions)} attractions")
        
        if attractions:
            sample_attraction = attractions[0]
            logger.info(f"Sample attraction: {sample_attraction.get('name', 'Unknown')}")
            
            # Test conversion to venue
            venue = hk_gov_service.convert_to_venue(sample_attraction)
            if venue:
                logger.info(f"✅ Successfully converted to venue: {venue.name}")
            else:
                logger.warning("❌ Failed to convert attraction to venue")
        
        # Test events
        logger.info("Testing HKTB events API...")
        events = hk_gov_service.get_hktb_events()
        logger.info(f"✅ Retrieved {len(events)} events")
        
        # Test restaurants
        logger.info("Testing restaurant licenses API...")
        restaurants = hk_gov_service.get_restaurant_licenses()
        logger.info(f"✅ Retrieved {len(restaurants)} restaurant licenses")
        
        # Test MTR accessibility
        logger.info("Testing MTR accessibility API...")
        mtr_data = hk_gov_service.get_mtr_accessibility_info()
        logger.info(f"✅ Retrieved MTR data with {len(mtr_data.get('stations', {}))} stations")
        
        # Test accessible facilities
        logger.info("Testing accessible facilities API...")
        facilities = hk_gov_service.get_accessible_facilities()
        logger.info(f"✅ Retrieved {len(facilities)} accessible facilities")
        
    except Exception as e:
        logger.error(f"❌ HK Government Data Service test failed: {str(e)}")
    
    # Test Facilities Service
    logger.info("Testing Facilities Service...")
    facilities_service = FacilitiesService()
    
    try:
        # Test public toilets
        toilets = facilities_service.get_public_toilets()
        logger.info(f"✅ Retrieved {len(toilets)} public toilets")
        
        # Test nearby facilities
        if toilets:
            nearby = facilities_service.get_nearby_facilities(22.2816, 114.1578, 1.0)
            logger.info(f"✅ Found {len(nearby)} facilities near Central")
        
        # Test accessibility facilities
        access_facilities = facilities_service.get_accessibility_facilities()
        logger.info(f"✅ Retrieved {len(access_facilities)} accessibility facilities")
        
    except Exception as e:
        logger.error(f"❌ Facilities Service test failed: {str(e)}")
    
    # Test Weather Service with HKO API
    logger.info("Testing Weather Service with HKO API...")
    weather_service = WeatherService()
    
    try:
        # Test current weather
        current_weather = weather_service.get_current_weather()
        logger.info(f"✅ Current weather: {current_weather.temperature}°C, {current_weather.weather_description}")
        
        # Test forecast
        forecast = weather_service.get_forecast(3)
        logger.info(f"✅ Retrieved {len(forecast)} day forecast")
        
    except Exception as e:
        logger.error(f"❌ Weather Service test failed: {str(e)}")
    
    logger.info("=== GOVERNMENT API INTEGRATION TEST COMPLETE ===")

if __name__ == "__main__":
    test_government_apis()