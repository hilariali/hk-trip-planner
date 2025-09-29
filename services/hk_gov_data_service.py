"""
Hong Kong Government Open Data Service
Integrates with various HK government APIs for attractions, events, and facilities
"""

import requests
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from models import Venue, VenueCategory, Location, AccessibilityInfo, DietaryOption, WeatherSuitability

# Configure logging
logger = logging.getLogger(__name__)

class HKGovDataService:
    """Service for fetching Hong Kong government open data"""
    
    def __init__(self):
        """Initialize HK government data service"""
        self.base_url = "https://data.gov.hk"
        self.timeout = 15
    
    def get_major_attractions(self) -> List[Dict]:
        """Get major attractions from HK Tourism Board"""
        try:
            # Major attractions API
            url = "https://www.discover.gov.hk/opendata/attractions.json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved {len(data)} major attractions from HK Tourism Board")
                return self._process_attractions_data(data)
            else:
                logger.warning(f"Attractions API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Could not fetch attractions data: {str(e)}")
            return []
    
    def get_hktb_events(self) -> List[Dict]:
        """Get events organized by Hong Kong Tourism Board"""
        try:
            # HKTB events API
            url = "https://data.gov.hk/en-data/api/get?id=hk-cstb-cstb_tc-tc-hktb-events&format=json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved {len(data)} HKTB events")
                return self._process_events_data(data)
            else:
                logger.warning(f"Events API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Could not fetch events data: {str(e)}")
            return []
    
    def get_restaurant_licenses(self) -> List[Dict]:
        """Get licensed restaurants from FEHD"""
        try:
            # Restaurant licenses API
            url = "https://data.gov.hk/en-data/api/get?id=hk-fehd-fehdlmis-restaurant-licences&format=json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved {len(data)} restaurant licenses")
                return self._process_restaurant_data(data)
            else:
                logger.warning(f"Restaurant API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Could not fetch restaurant data: {str(e)}")
            return []
    
    def get_mtr_accessibility_info(self) -> Dict:
        """Get MTR routes and barrier-free facilities"""
        try:
            # MTR accessibility API
            url = "https://data.gov.hk/en-data/api/get?id=mtr-data-routes-fares-barrier-free-facilities&format=json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved MTR accessibility data")
                return self._process_mtr_data(data)
            else:
                logger.warning(f"MTR API returned status {response.status_code}")
                return {}
                
        except Exception as e:
            logger.warning(f"Could not fetch MTR data: {str(e)}")
            return {}
    
    def get_accessible_facilities(self) -> List[Dict]:
        """Get accessible facilities from Hong Kong Rehabilitation Society"""
        try:
            # Accessible facilities API
            url = "https://data.gov.hk/en-data/api/get?id=rehabsociety-access-accessibile-facilities&format=json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved {len(data)} accessible facilities")
                return self._process_accessibility_data(data)
            else:
                logger.warning(f"Accessibility API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Could not fetch accessibility data: {str(e)}")
            return []
    
    def _process_attractions_data(self, data: List[Dict]) -> List[Dict]:
        """Process attractions data into standardized format"""
        processed = []
        
        for attraction in data:
            try:
                processed_attraction = {
                    'id': f"hktb_{attraction.get('id', len(processed))}",
                    'name': attraction.get('name_en', attraction.get('name', 'Unknown Attraction')),
                    'name_zh': attraction.get('name_zh', ''),
                    'category': 'attraction',
                    'description': attraction.get('description_en', attraction.get('description', '')),
                    'district': attraction.get('district_en', attraction.get('district', '')),
                    'address': attraction.get('address_en', attraction.get('address', '')),
                    'latitude': float(attraction.get('latitude', 0)) if attraction.get('latitude') else None,
                    'longitude': float(attraction.get('longitude', 0)) if attraction.get('longitude') else None,
                    'phone': attraction.get('phone', ''),
                    'website': attraction.get('website', ''),
                    'opening_hours': attraction.get('opening_hours', {}),
                    'admission_fee': attraction.get('admission_fee', ''),
                    'accessibility_info': attraction.get('accessibility', {}),
                    'source': 'hktb_attractions'
                }
                processed.append(processed_attraction)
                
            except Exception as e:
                logger.warning(f"Error processing attraction {attraction}: {str(e)}")
                continue
        
        return processed
    
    def _process_events_data(self, data: List[Dict]) -> List[Dict]:
        """Process HKTB events data"""
        processed = []
        current_date = datetime.now()
        
        for event in data:
            try:
                # Only include future events
                event_date = datetime.strptime(event.get('date', ''), '%Y-%m-%d') if event.get('date') else current_date
                if event_date < current_date:
                    continue
                
                processed_event = {
                    'id': f"hktb_event_{event.get('id', len(processed))}",
                    'name': event.get('name_en', event.get('name', 'Unknown Event')),
                    'name_zh': event.get('name_zh', ''),
                    'category': 'event',
                    'description': event.get('description_en', event.get('description', '')),
                    'venue': event.get('venue_en', event.get('venue', '')),
                    'district': event.get('district_en', event.get('district', '')),
                    'date': event.get('date', ''),
                    'time': event.get('time', ''),
                    'admission': event.get('admission', 'Free'),
                    'website': event.get('website', ''),
                    'source': 'hktb_events'
                }
                processed.append(processed_event)
                
            except Exception as e:
                logger.warning(f"Error processing event {event}: {str(e)}")
                continue
        
        return processed
    
    def _process_restaurant_data(self, data: List[Dict]) -> List[Dict]:
        """Process restaurant license data"""
        processed = []
        
        for restaurant in data:
            try:
                processed_restaurant = {
                    'id': f"fehd_{restaurant.get('licence_no', len(processed))}",
                    'name': restaurant.get('name_en', restaurant.get('name', 'Unknown Restaurant')),
                    'name_zh': restaurant.get('name_zh', ''),
                    'category': 'restaurant',
                    'district': restaurant.get('district_en', restaurant.get('district', '')),
                    'address': restaurant.get('address_en', restaurant.get('address', '')),
                    'licence_type': restaurant.get('licence_type', ''),
                    'licence_no': restaurant.get('licence_no', ''),
                    'source': 'fehd_licenses'
                }
                processed.append(processed_restaurant)
                
            except Exception as e:
                logger.warning(f"Error processing restaurant {restaurant}: {str(e)}")
                continue
        
        return processed
    
    def _process_mtr_data(self, data: Dict) -> Dict:
        """Process MTR accessibility data"""
        try:
            processed = {
                'stations': {},
                'lines': {},
                'accessibility_features': {}
            }
            
            # Process station accessibility info
            if 'stations' in data:
                for station in data['stations']:
                    station_code = station.get('code', '')
                    processed['stations'][station_code] = {
                        'name_en': station.get('name_en', ''),
                        'name_zh': station.get('name_zh', ''),
                        'has_lift': station.get('has_lift', False),
                        'has_tactile_guide': station.get('has_tactile_guide', False),
                        'has_audio_announcement': station.get('has_audio_announcement', False),
                        'wheelchair_accessible': station.get('wheelchair_accessible', False),
                        'step_free_access': station.get('step_free_access', False)
                    }
            
            return processed
            
        except Exception as e:
            logger.warning(f"Error processing MTR data: {str(e)}")
            return {}
    
    def _process_accessibility_data(self, data: List[Dict]) -> List[Dict]:
        """Process accessibility facilities data"""
        processed = []
        
        for facility in data:
            try:
                processed_facility = {
                    'id': f"rehab_{facility.get('id', len(processed))}",
                    'name': facility.get('name_en', facility.get('name', 'Unknown Facility')),
                    'name_zh': facility.get('name_zh', ''),
                    'category': facility.get('category', 'facility'),
                    'district': facility.get('district_en', facility.get('district', '')),
                    'address': facility.get('address_en', facility.get('address', '')),
                    'latitude': float(facility.get('latitude', 0)) if facility.get('latitude') else None,
                    'longitude': float(facility.get('longitude', 0)) if facility.get('longitude') else None,
                    'accessibility_features': {
                        'wheelchair_accessible': facility.get('wheelchair_accessible', False),
                        'has_lift': facility.get('has_lift', False),
                        'accessible_toilet': facility.get('accessible_toilet', False),
                        'accessible_parking': facility.get('accessible_parking', False),
                        'braille_signage': facility.get('braille_signage', False),
                        'hearing_loop': facility.get('hearing_loop', False)
                    },
                    'source': 'rehab_society'
                }
                processed.append(processed_facility)
                
            except Exception as e:
                logger.warning(f"Error processing accessibility facility {facility}: {str(e)}")
                continue
        
        return processed
    
    def convert_to_venue(self, gov_data: Dict) -> Optional[Venue]:
        """Convert government data to Venue object"""
        try:
            # Create location
            location = Location(
                latitude=gov_data.get('latitude', 0.0) or 0.0,
                longitude=gov_data.get('longitude', 0.0) or 0.0,
                address=gov_data.get('address', ''),
                district=gov_data.get('district', '')
            )
            
            # Create accessibility info
            accessibility_data = gov_data.get('accessibility_features', gov_data.get('accessibility_info', {}))
            accessibility = AccessibilityInfo(
                has_elevator=accessibility_data.get('has_lift', False),
                wheelchair_accessible=accessibility_data.get('wheelchair_accessible', False),
                accessible_toilets=accessibility_data.get('accessible_toilet', False),
                step_free_access=accessibility_data.get('step_free_access', False),
                parent_facilities=False,  # Not available in gov data
                rest_areas=False,  # Not available in gov data
                difficulty_level=1,  # Default
                accessibility_notes=[]
            )
            
            # Create dietary options (mostly for restaurants)
            dietary_options = DietaryOption(
                soft_meals=False,  # Need to enhance with additional data
                vegetarian=False,
                halal=False,
                no_seafood=False,
                allergy_friendly=False,
                dietary_notes=[]
            )
            
            # Determine category
            category_mapping = {
                'attraction': VenueCategory.ATTRACTION,
                'restaurant': VenueCategory.RESTAURANT,
                'event': VenueCategory.ATTRACTION,  # Events as attractions
                'facility': VenueCategory.ATTRACTION,
                'museum': VenueCategory.MUSEUM,
                'park': VenueCategory.PARK
            }
            
            category = category_mapping.get(gov_data.get('category', 'attraction'), VenueCategory.ATTRACTION)
            
            # Estimate cost range (since not provided in gov data)
            cost_range = self._estimate_cost_range(category, gov_data)
            
            return Venue(
                id=gov_data.get('id', ''),
                name=gov_data.get('name', ''),
                category=category,
                location=location,
                accessibility=accessibility,
                dietary_options=dietary_options,
                cost_range=cost_range,
                opening_hours=gov_data.get('opening_hours', {}),
                weather_suitability=WeatherSuitability.MIXED,
                description=gov_data.get('description', ''),
                phone=gov_data.get('phone', ''),
                website=gov_data.get('website', ''),
                elderly_discount=False,  # Need to enhance
                child_discount=False   # Need to enhance
            )
            
        except Exception as e:
            logger.warning(f"Error converting gov data to venue: {str(e)}")
            return None
    
    def _estimate_cost_range(self, category: VenueCategory, data: Dict) -> Tuple[int, int]:
        """Estimate cost range based on venue type and available data"""
        admission_fee = data.get('admission_fee', '').lower()
        
        # Check if free
        if 'free' in admission_fee or admission_fee == '':
            return (0, 0)
        
        # Default ranges by category
        if category == VenueCategory.ATTRACTION:
            return (20, 100)  # HKD
        elif category == VenueCategory.MUSEUM:
            return (10, 50)
        elif category == VenueCategory.RESTAURANT:
            return (50, 200)
        elif category == VenueCategory.PARK:
            return (0, 0)
        else:
            return (0, 50)