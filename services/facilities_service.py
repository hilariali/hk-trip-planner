"""
Facilities Service for Hong Kong Trip Planner
Handles public toilets, accessibility facilities, and other amenities
"""

import requests
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger('services.facilities_service')

@dataclass
class PublicFacility:
    """Public facility information"""
    id: str
    name: str
    category: str  # 'toilet', 'rest_area', 'accessibility'
    latitude: float
    longitude: float
    address: str
    district: str
    accessibility_features: Dict[str, bool]
    opening_hours: str = ""
    notes: str = ""

class FacilitiesService:
    """Service for managing public facilities and amenities"""
    
    def __init__(self):
        """Initialize facilities service"""
        self.timeout = 10
    
    def get_public_toilets(self, district: Optional[str] = None) -> List[PublicFacility]:
        """Get public toilets information"""
        try:
            # Note: This would use the Toilet Rush API or similar
            # For now, we'll return some sample data
            toilets = self._get_sample_toilets()
            
            if district:
                toilets = [t for t in toilets if t.district.lower() == district.lower()]
            
            logger.info(f"Retrieved {len(toilets)} public toilets")
            return toilets
            
        except Exception as e:
            logger.warning(f"Could not fetch toilet data: {str(e)}")
            return []
    
    def get_nearby_facilities(self, latitude: float, longitude: float, 
                            radius_km: float = 1.0) -> List[PublicFacility]:
        """Get facilities near a specific location"""
        try:
            all_facilities = self.get_public_toilets()
            nearby = []
            
            for facility in all_facilities:
                distance = self._calculate_distance(
                    latitude, longitude, 
                    facility.latitude, facility.longitude
                )
                
                if distance <= radius_km:
                    nearby.append(facility)
            
            logger.info(f"Found {len(nearby)} facilities within {radius_km}km")
            return nearby
            
        except Exception as e:
            logger.warning(f"Error finding nearby facilities: {str(e)}")
            return []
    
    def get_accessibility_facilities(self) -> List[PublicFacility]:
        """Get specialized accessibility facilities"""
        try:
            # This would integrate with HK Rehabilitation Society data
            facilities = self._get_sample_accessibility_facilities()
            
            logger.info(f"Retrieved {len(facilities)} accessibility facilities")
            return facilities
            
        except Exception as e:
            logger.warning(f"Could not fetch accessibility facilities: {str(e)}")
            return []
    
    def _get_sample_toilets(self) -> List[PublicFacility]:
        """Get sample public toilet data (to be replaced with real API)"""
        return [
            PublicFacility(
                id="toilet_001",
                name="Central MTR Station Public Toilet",
                category="toilet",
                latitude=22.2816,
                longitude=114.1578,
                address="Central MTR Station, Central",
                district="Central and Western",
                accessibility_features={
                    "wheelchair_accessible": True,
                    "baby_changing": True,
                    "accessible_toilet": True,
                    "grab_rails": True
                },
                opening_hours="24 hours",
                notes="Located near Exit A"
            ),
            PublicFacility(
                id="toilet_002", 
                name="Tsim Sha Tsui Promenade Public Toilet",
                category="toilet",
                latitude=22.2942,
                longitude=114.1722,
                address="Tsim Sha Tsui Promenade, Tsim Sha Tsui",
                district="Yau Tsim Mong",
                accessibility_features={
                    "wheelchair_accessible": True,
                    "baby_changing": True,
                    "accessible_toilet": True,
                    "grab_rails": True
                },
                opening_hours="06:00-23:00",
                notes="Near the Star Ferry Pier"
            ),
            PublicFacility(
                id="toilet_003",
                name="Hong Kong Park Public Toilet",
                category="toilet", 
                latitude=22.2769,
                longitude=114.1628,
                address="Hong Kong Park, Central",
                district="Central and Western",
                accessibility_features={
                    "wheelchair_accessible": True,
                    "baby_changing": False,
                    "accessible_toilet": True,
                    "grab_rails": True
                },
                opening_hours="06:00-23:00",
                notes="Near the main entrance"
            ),
            PublicFacility(
                id="toilet_004",
                name="Victoria Peak Public Toilet",
                category="toilet",
                latitude=22.2711,
                longitude=114.1489,
                address="The Peak, Hong Kong Island",
                district="Central and Western",
                accessibility_features={
                    "wheelchair_accessible": False,
                    "baby_changing": True,
                    "accessible_toilet": False,
                    "grab_rails": True
                },
                opening_hours="08:00-22:00",
                notes="Limited accessibility due to terrain"
            )
        ]
    
    def _get_sample_accessibility_facilities(self) -> List[PublicFacility]:
        """Get sample accessibility facility data"""
        return [
            PublicFacility(
                id="access_001",
                name="Central Library Accessibility Center",
                category="accessibility",
                latitude=22.2783,
                longitude=114.1747,
                address="66 Causeway Road, Causeway Bay",
                district="Wan Chai",
                accessibility_features={
                    "wheelchair_accessible": True,
                    "braille_materials": True,
                    "hearing_loop": True,
                    "accessible_computer": True,
                    "rest_area": True
                },
                opening_hours="09:00-20:00 (Mon-Sat), 13:00-17:00 (Sun)",
                notes="Full accessibility services available"
            ),
            PublicFacility(
                id="access_002",
                name="Hong Kong Space Museum Accessibility Services",
                category="accessibility",
                latitude=22.2942,
                longitude=114.1722,
                address="10 Salisbury Road, Tsim Sha Tsui",
                district="Yau Tsim Mong",
                accessibility_features={
                    "wheelchair_accessible": True,
                    "audio_guide": True,
                    "tactile_exhibits": True,
                    "accessible_parking": True,
                    "rest_area": True
                },
                opening_hours="10:00-21:00 (Mon, Wed-Fri), 10:00-21:00 (Sat-Sun)",
                notes="Closed on Tuesdays except public holidays"
            )
        ]
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points in kilometers using Haversine formula"""
        import math
        
        # Convert latitude and longitude from degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        # Radius of earth in kilometers
        r = 6371
        
        return c * r
    
    def find_facilities_along_route(self, waypoints: List[Tuple[float, float]], 
                                  facility_type: str = "toilet") -> List[PublicFacility]:
        """Find facilities along a route defined by waypoints"""
        try:
            all_facilities = []
            
            if facility_type == "toilet":
                all_facilities = self.get_public_toilets()
            elif facility_type == "accessibility":
                all_facilities = self.get_accessibility_facilities()
            
            route_facilities = []
            
            for waypoint in waypoints:
                nearby = self.get_nearby_facilities(
                    waypoint[0], waypoint[1], radius_km=0.5
                )
                route_facilities.extend(nearby)
            
            # Remove duplicates
            unique_facilities = []
            seen_ids = set()
            
            for facility in route_facilities:
                if facility.id not in seen_ids:
                    unique_facilities.append(facility)
                    seen_ids.add(facility.id)
            
            logger.info(f"Found {len(unique_facilities)} facilities along route")
            return unique_facilities
            
        except Exception as e:
            logger.warning(f"Error finding facilities along route: {str(e)}")
            return []
    
    def get_facility_recommendations(self, user_needs: List[str]) -> List[PublicFacility]:
        """Get facility recommendations based on user needs"""
        try:
            all_facilities = self.get_public_toilets() + self.get_accessibility_facilities()
            recommended = []
            
            for facility in all_facilities:
                score = 0
                
                # Score based on user needs
                if "wheelchair" in user_needs and facility.accessibility_features.get("wheelchair_accessible"):
                    score += 3
                if "baby_changing" in user_needs and facility.accessibility_features.get("baby_changing"):
                    score += 2
                if "rest_area" in user_needs and facility.accessibility_features.get("rest_area"):
                    score += 2
                if "hearing_aid" in user_needs and facility.accessibility_features.get("hearing_loop"):
                    score += 2
                
                if score > 0:
                    recommended.append(facility)
            
            # Sort by score (highest first)
            recommended.sort(key=lambda f: sum(f.accessibility_features.values()), reverse=True)
            
            logger.info(f"Recommended {len(recommended)} facilities based on user needs")
            return recommended
            
        except Exception as e:
            logger.warning(f"Error getting facility recommendations: {str(e)}")
            return []