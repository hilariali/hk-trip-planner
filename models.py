"""
Data models for Hong Kong Trip Planner
Core data structures for venues, preferences, and itineraries
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
from enum import Enum
from datetime import datetime

class VenueCategory(Enum):
    """Categories of venues available in Hong Kong"""
    ATTRACTION = "attraction"
    RESTAURANT = "restaurant" 
    TRANSPORT = "transport"
    SHOPPING = "shopping"
    PARK = "park"
    MUSEUM = "museum"

class WeatherSuitability(Enum):
    """Weather suitability for venues"""
    INDOOR = "indoor"
    OUTDOOR = "outdoor"
    MIXED = "mixed"

@dataclass
class Location:
    """Geographic location with coordinates"""
    latitude: float
    longitude: float
    address: str = ""
    district: str = ""

@dataclass
class AccessibilityInfo:
    """Comprehensive accessibility information for venues"""
    has_elevator: bool = False
    wheelchair_accessible: bool = False
    accessible_toilets: bool = False
    step_free_access: bool = False
    parent_facilities: bool = False
    rest_areas: bool = False
    difficulty_level: int = 1  # 1-5 scale (1=very easy, 5=very difficult)
    accessibility_notes: List[str] = field(default_factory=list)

@dataclass
class DietaryOption:
    """Dietary options available at venues"""
    soft_meals: bool = False
    vegetarian: bool = False
    halal: bool = False
    no_seafood: bool = False
    allergy_friendly: bool = False
    dietary_notes: List[str] = field(default_factory=list)

@dataclass
class Venue:
    """Complete venue information with accessibility and dietary data"""
    id: str
    name: str
    category: VenueCategory
    location: Location
    accessibility: AccessibilityInfo
    dietary_options: DietaryOption
    cost_range: Tuple[int, int]  # (min_cost, max_cost) in HKD
    opening_hours: Dict[str, str] = field(default_factory=dict)
    weather_suitability: WeatherSuitability = WeatherSuitability.MIXED
    description: str = ""
    phone: str = ""
    website: str = ""
    elderly_discount: bool = False
    child_discount: bool = False

@dataclass
class UserPreferences:
    """User preferences and requirements for trip planning"""
    family_composition: Dict[str, int]  # {'adults': 2, 'children': 1, 'seniors': 1}
    mobility_needs: List[str]  # ['wheelchair', 'elevator_only', 'avoid_stairs']
    dietary_restrictions: List[str]  # ['soft_meals', 'vegetarian', 'allergies']
    budget_range: Tuple[int, int]  # (min_per_person, max_per_person) per day
    trip_duration: int  # days
    transportation_preference: List[str]  # ['mtr', 'taxi', 'bus']
    
    def total_people(self) -> int:
        """Calculate total number of people in the group"""
        return sum(self.family_composition.values())
    
    def has_seniors(self) -> bool:
        """Check if group includes seniors"""
        return self.family_composition.get('seniors', 0) > 0
    
    def has_children(self) -> bool:
        """Check if group includes children"""
        return self.family_composition.get('children', 0) > 0
    
    def requires_accessibility(self) -> bool:
        """Check if group has accessibility requirements"""
        return len(self.mobility_needs) > 0

@dataclass
class TransportSegment:
    """Transportation between venues"""
    origin: str
    destination: str
    mode: str  # 'mtr', 'bus', 'taxi', 'walking'
    duration_minutes: int
    cost: float
    accessibility_notes: List[str] = field(default_factory=list)

@dataclass
class DayPlan:
    """Complete plan for a single day"""
    day: int
    venues: List[Venue]
    transportation: List[TransportSegment]
    estimated_cost: float
    total_walking_distance: float  # in kilometers
    accessibility_notes: List[str] = field(default_factory=list)
    weather_considerations: List[str] = field(default_factory=list)

@dataclass
class CostBreakdown:
    """Detailed cost breakdown for the trip"""
    attractions: float
    meals: float
    transportation: float
    total: float
    discounts_applied: float = 0.0
    cost_per_person: float = 0.0

@dataclass
class Itinerary:
    """Complete trip itinerary with all days and metadata"""
    day_plans: List[DayPlan]
    total_cost: float
    cost_breakdown: CostBreakdown
    accessibility_score: float  # 1-5 rating of overall accessibility
    generated_at: datetime = field(default_factory=datetime.now)
    user_preferences: Optional[UserPreferences] = None
    
    def get_total_venues(self) -> int:
        """Get total number of venues across all days"""
        return sum(len(day.venues) for day in self.day_plans)
    
    def get_average_daily_cost(self) -> float:
        """Calculate average cost per day"""
        return self.total_cost / len(self.day_plans) if self.day_plans else 0

@dataclass
class WeatherData:
    """Weather information for trip planning"""
    temperature: float
    humidity: float
    rainfall_probability: float
    weather_description: str
    is_suitable_for_outdoor: bool = True
    date: datetime = field(default_factory=datetime.now)

@dataclass
class SearchCriteria:
    """Criteria for searching venues"""
    categories: List[VenueCategory] = field(default_factory=list)
    accessibility_required: List[str] = field(default_factory=list)
    dietary_required: List[str] = field(default_factory=list)
    max_cost: Optional[int] = None
    weather_suitability: Optional[WeatherSuitability] = None
    district: Optional[str] = None