#!/usr/bin/env python3
"""
Test script for AI venue service
"""

import logging
from services.ai_venue_service import AIVenueService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_ai_service')

def test_ai_service_without_key():
    """Test AI service without API key (should use fallbacks)"""
    logger.info("=== Testing AI Service Without API Key ===")
    
    ai_service = AIVenueService()
    stats = ai_service.get_service_stats()
    
    logger.info(f"Service version: {stats['version']}")
    logger.info(f"Client available: {stats['client_available']}")
    logger.info(f"API key set: {stats['api_key_set']}")
    
    # Test venue generation (should use fallbacks)
    preferences = {
        'family_composition': {'adults': 2, 'children': 1, 'seniors': 1},
        'mobility_needs': ['wheelchair', 'elevator_only'],
        'dietary_restrictions': ['soft_meals'],
        'budget_range': (300, 800),
        'trip_duration': 2
    }
    
    venues = ai_service.generate_venues_for_preferences(preferences)
    logger.info(f"Generated {len(venues)} venues (fallback mode)")
    
    for venue in venues:
        logger.info(f"  - {venue['name']} ({venue['category']})")

def test_ai_service_with_key():
    """Test AI service with API key"""
    logger.info("=== Testing AI Service With API Key ===")
    
    # This would be called with a real API key
    # ai_service = AIVenueService("your-api-key-here")
    
    logger.info("To test with API key, call:")
    logger.info("ai_service = AIVenueService('your-api-key')")
    logger.info("venues = ai_service.generate_venues_for_preferences(preferences)")

def test_venue_service_integration():
    """Test integration with venue service"""
    logger.info("=== Testing Venue Service Integration ===")
    
    try:
        from services.venue_service import VenueService
        
        venue_service = VenueService()
        
        # Test without AI key
        all_venues = venue_service.get_all_venues()
        logger.info(f"Standard venues: {len(all_venues)}")
        
        # Test AI service availability
        ai_service = venue_service._get_ai_service()
        if ai_service:
            logger.info("AI service integrated successfully")
            stats = ai_service.get_service_stats()
            logger.info(f"AI service stats: {stats}")
        else:
            logger.warning("AI service not available")
        
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}")

def main():
    """Run all tests"""
    test_ai_service_without_key()
    test_ai_service_with_key()
    test_venue_service_integration()

if __name__ == "__main__":
    main()