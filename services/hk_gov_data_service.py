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
logger = logging.getLogger('services.hk_gov_data_service')

class HKGovDataService:
    """Service for fetching Hong Kong government open data"""
    
    def __init__(self):
        """Initialize HK government data service"""
        self.base_url = "https://data.gov.hk"
        self.timeout = 5  # Reduced timeout to fail faster
        self._api_available = True  # Track if APIs are working
    
    def get_major_attractions(self) -> List[Dict]:
        """Get major attractions from HK Tourism Board CSV"""
        if not self._api_available:
            return []  # Skip if APIs are known to be down
            
        try:
            # Use official HK Tourism Board CSV endpoint
            url = "https://www.tourism.gov.hk/datagovhk/major_attractions/major_attractions_info_en.csv"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse CSV data
                import csv
                import io
                
                csv_data = response.text
                reader = csv.DictReader(io.StringIO(csv_data))
                attractions = list(reader)
                
                logger.info(f"Retrieved {len(attractions)} major attractions from HK Tourism Board CSV")
                self._api_available = True
                return self._process_attractions_csv_data(attractions)
            else:
                if response.status_code == 404:
                    self._api_available = False  # Mark as unavailable
                logger.warning(f"Attractions CSV API returned status {response.status_code}")
                return []
                
        except Exception as e:
            self._api_available = False  # Mark as unavailable on network errors
            logger.warning(f"Could not fetch attractions CSV data: {str(e)}")
            return []
    
    def get_hktb_events(self) -> List[Dict]:
        """Get events organized by Hong Kong Tourism Board"""
        if not self._api_available:
            return []  # Skip if APIs are known to be down
            
        try:
            # HKTB events API
            url = "https://data.gov.hk/en-data/api/get?id=hk-cstb-cstb_tc-tc-hktb-events&format=json"
            response = requests.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Retrieved {len(data)} HKTB events")
                return self._process_events_data(data)
            else:
                if response.status_code == 404:
                    logger.info("Events API not available (404) - using local data only")
                else:
                    logger.warning(f"Events API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Could not fetch events data: {str(e)}")
            return []
    
    def get_restaurant_licenses(self) -> List[Dict]:
        """Get licensed restaurants from FEHD XML"""
        try:
            # Use official FEHD restaurant licenses XML endpoint
            url = "https://res.data.gov.hk/api/get-download-file?name=https%3A%2F%2Fwww.fehd.gov.hk%2Fenglish%2Flicensing%2Flicense%2Ftext%2FLP_Restaurants_EN.XML"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse XML data
                import xml.etree.ElementTree as ET
                
                root = ET.fromstring(response.content)
                restaurants = self._parse_restaurant_xml(root)
                
                logger.info(f"Retrieved {len(restaurants)} restaurant licenses from FEHD XML")
                return restaurants
            else:
                logger.warning(f"Restaurant XML API returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.warning(f"Could not fetch restaurant XML data: {str(e)}")
            return []
    
    def get_mtr_accessibility_info(self) -> Dict:
        """Get MTR routes and barrier-free facilities from official CSV"""
        try:
            # Get MTR lines and stations
            stations_url = "https://opendata.mtr.com.hk/data/mtr_lines_and_stations.csv"
            facilities_url = "https://opendata.mtr.com.hk/data/barrier_free_facilities.csv"
            
            stations_response = requests.get(stations_url, timeout=10)
            facilities_response = requests.get(facilities_url, timeout=10)
            
            if stations_response.status_code == 200 and facilities_response.status_code == 200:
                import csv
                import io
                
                # Parse stations CSV
                stations_reader = csv.DictReader(io.StringIO(stations_response.text))
                stations = list(stations_reader)
                
                # Parse facilities CSV
                facilities_reader = csv.DictReader(io.StringIO(facilities_response.text))
                facilities = list(facilities_reader)
                
                logger.info(f"Retrieved {len(stations)} MTR stations and {len(facilities)} accessibility facilities")
                return self._process_mtr_csv_data(stations, facilities)
            else:
                logger.warning(f"MTR CSV APIs returned status {stations_response.status_code}, {facilities_response.status_code}")
                return {}
                
        except Exception as e:
            logger.warning(f"Could not fetch MTR CSV data: {str(e)}")
            return {}
    
    def get_accessible_facilities(self) -> List[Dict]:
        """Get accessible facilities from Hong Kong Rehabilitation Society XML"""
        if not self._api_available:
            return []  # Skip if APIs are known to be down
            
        try:
            # Use official accessibility XML endpoints
            attractions_url = "https://res.data.gov.hk/api/get-download-file?name=https%3A%2F%2Faccessguide.hk%2F%3Ffeed%3Datom%26post_type%3Dlocation%26type%3Dattractions"
            dining_url = "https://res.data.gov.hk/api/get-download-file?name=https%3A%2F%2Faccessguide.hk%2F%3Ffeed%3Datom%26post_type%3Dlocation%26type%3Dshopping-dining"
            
            facilities = []
            
            # Get accessible attractions
            try:
                attractions_response = requests.get(attractions_url, timeout=10)
                if attractions_response.status_code == 200:
                    attractions_facilities = self._parse_accessibility_xml(attractions_response.content, 'attractions')
                    facilities.extend(attractions_facilities)
            except Exception as e:
                logger.warning(f"Could not fetch accessible attractions XML: {str(e)}")
            
            # Get accessible dining/shopping
            try:
                dining_response = requests.get(dining_url, timeout=10)
                if dining_response.status_code == 200:
                    dining_facilities = self._parse_accessibility_xml(dining_response.content, 'dining')
                    facilities.extend(dining_facilities)
            except Exception as e:
                logger.warning(f"Could not fetch accessible dining XML: {str(e)}")
            
            logger.info(f"Retrieved {len(facilities)} accessible facilities from XML feeds")
            return facilities
                
        except Exception as e:
            logger.warning(f"Could not fetch accessibility XML data: {str(e)}")
            return []
    
    def _process_attractions_csv_data(self, data: List[Dict]) -> List[Dict]:
        """Process attractions CSV data into standardized format"""
        processed = []
        
        for attraction in data:
            try:
                processed_attraction = {
                    'id': f"hktb_{len(processed)}",
                    'name': attraction.get('Attraction', attraction.get('Name (English)', 'Unknown Attraction')),
                    'name_zh': attraction.get('Name (Traditional Chinese)', ''),
                    'category': 'attraction',
                    'description': attraction.get('Description', ''),
                    'district': '',  # Not available in this CSV format
                    'address': attraction.get('Address', ''),
                    'latitude': None,  # Parse from coordinates field
                    'longitude': None,  # Parse from coordinates field
                    'phone': attraction.get('Telephone number', ''),
                    'website': attraction.get('Website', ''),
                    'opening_hours': '',
                    'admission_fee': '',
                    'accessibility_info': {},  # Will be enhanced with additional data
                    'source': 'hktb_attractions_csv'
                }
                
                # Parse coordinates if available
                coords = attraction.get('Latitude and longitude coordinates', '')
                if coords and ',' in coords:
                    try:
                        lat_str, lng_str = coords.split(',')
                        processed_attraction['latitude'] = float(lat_str.strip())
                        processed_attraction['longitude'] = float(lng_str.strip())
                    except:
                        pass
                processed.append(processed_attraction)
                
            except Exception as e:
                logger.warning(f"Error processing attraction CSV {attraction}: {str(e)}")
                continue
        
        return processed

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
   
    def _parse_restaurant_xml(self, root) -> List[Dict]:
        """Parse FEHD restaurant XML data"""
        restaurants = []
        
        try:
            # Navigate XML structure - adjust based on actual XML format
            for restaurant_elem in root.findall('.//restaurant') or root.findall('.//licence'):
                try:
                    restaurant = {
                        'id': f"fehd_{len(restaurants)}",
                        'name': self._get_xml_text(restaurant_elem, 'name') or self._get_xml_text(restaurant_elem, 'licensee_name'),
                        'category': 'restaurant',
                        'district': self._get_xml_text(restaurant_elem, 'district'),
                        'address': self._get_xml_text(restaurant_elem, 'address'),
                        'licence_type': self._get_xml_text(restaurant_elem, 'licence_type'),
                        'licence_no': self._get_xml_text(restaurant_elem, 'licence_no'),
                        'source': 'fehd_xml'
                    }
                    restaurants.append(restaurant)
                except Exception as e:
                    logger.warning(f"Error parsing restaurant XML element: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error parsing restaurant XML: {str(e)}")
        
        return restaurants
    
    def _parse_accessibility_xml(self, xml_content: bytes, facility_type: str) -> List[Dict]:
        """Parse accessibility XML data from Hong Kong Rehabilitation Society"""
        facilities = []
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
            
            # Handle Atom feed format
            for entry in root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                try:
                    facility = {
                        'id': f"rehab_{facility_type}_{len(facilities)}",
                        'name': self._get_xml_text(entry, '{http://www.w3.org/2005/Atom}title'),
                        'category': facility_type,
                        'description': self._get_xml_text(entry, '{http://www.w3.org/2005/Atom}content'),
                        'link': self._get_xml_attr(entry, '{http://www.w3.org/2005/Atom}link', 'href'),
                        'accessibility_features': {
                            'wheelchair_accessible': True,  # Assume true for rehab society data
                            'has_lift': False,  # Will be parsed from content if available
                            'accessible_toilet': False,
                            'accessible_parking': False
                        },
                        'source': f'rehab_society_{facility_type}'
                    }
                    
                    # Try to extract more details from content
                    content = facility.get('description', '').lower()
                    if 'lift' in content or 'elevator' in content:
                        facility['accessibility_features']['has_lift'] = True
                    if 'toilet' in content:
                        facility['accessibility_features']['accessible_toilet'] = True
                    if 'parking' in content:
                        facility['accessibility_features']['accessible_parking'] = True
                    
                    facilities.append(facility)
                    
                except Exception as e:
                    logger.warning(f"Error parsing accessibility XML entry: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.warning(f"Error parsing accessibility XML: {str(e)}")
        
        return facilities
    
    def _process_mtr_csv_data(self, stations: List[Dict], facilities: List[Dict]) -> Dict:
        """Process MTR CSV data"""
        try:
            processed = {
                'stations': {},
                'lines': {},
                'accessibility_features': {}
            }
            
            # Process stations
            for station in stations:
                station_code = station.get('Station Code', station.get('Code', ''))
                if station_code:
                    processed['stations'][station_code] = {
                        'name_en': station.get('Station Name (English)', station.get('Name', '')),
                        'name_zh': station.get('Station Name (Chinese)', ''),
                        'line': station.get('Line', ''),
                        'wheelchair_accessible': False,  # Will be updated from facilities
                        'has_lift': False,
                        'step_free_access': False
                    }
            
            # Process accessibility facilities
            for facility in facilities:
                station_code = facility.get('Station Code', '')
                if station_code in processed['stations']:
                    facility_type = facility.get('Facility Type', '').lower()
                    if 'lift' in facility_type or 'elevator' in facility_type:
                        processed['stations'][station_code]['has_lift'] = True
                        processed['stations'][station_code]['wheelchair_accessible'] = True
                        processed['stations'][station_code]['step_free_access'] = True
            
            return processed
            
        except Exception as e:
            logger.warning(f"Error processing MTR CSV data: {str(e)}")
            return {}
    
    def _get_xml_text(self, element, tag_name: str) -> str:
        """Safely get text from XML element"""
        try:
            elem = element.find(tag_name)
            return elem.text if elem is not None and elem.text else ''
        except:
            return ''
    
    def _get_xml_attr(self, element, tag_name: str, attr_name: str) -> str:
        """Safely get attribute from XML element"""
        try:
            elem = element.find(tag_name)
            return elem.get(attr_name) if elem is not None else ''
        except:
            return ''