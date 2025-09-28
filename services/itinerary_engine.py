"""
Itinerary Engine for Hong Kong Trip Planner
AI-powered itinerary generation with accessibility focus
"""

import random
from typing import List, Dict, Tuple
from datetime import datetime, timedelta
from models import (
    UserPreferences, WeatherData, Itinerary, DayPlan, Venue, 
    VenueCategory, SearchCriteria, CostBreakdown, TransportSegment,
    WeatherSuitability
)
from services.venue_service import VenueService

class ItineraryEngine:
    """AI-powered engine for generating accessible itineraries"""
    
    def __init__(self):
        """Initialize itinerary engine"""
        self.venue_service = VenueService()
        self.max_venues_per_day = 3
        self.max_walking_distance = 2.0  # km per day for seniors/families
    
    def generate_itinerary(self, preferences: UserPreferences, weather_data: WeatherData) -> Itinerary:
        """Generate complete itinerary based on preferences and weather"""
        
        # Get suitable venues based on preferences
        suitable_venues = self._get_suitable_venues(preferences, weather_data)
        
        if not suitable_venues:
            raise Exception("No suitable venues found for your requirements")
        
        # Generate day plans
        day_plans = []
        used_venues = set()
        
        for day in range(1, preferences.trip_duration + 1):
            day_plan = self._generate_day_plan(
                day, preferences, weather_data, suitable_venues, used_venues
            )
            day_plans.append(day_plan)
        
        # Calculate costs and create itinerary
        total_cost, cost_breakdown = self._calculate_total_cost(day_plans, preferences)
        accessibility_score = self._calculate_accessibility_score(day_plans, preferences)
        
        return Itinerary(
            day_plans=day_plans,
            total_cost=total_cost,
            cost_breakdown=cost_breakdown,
            accessibility_score=accessibility_score,
            user_preferences=preferences
        )
    
    def _get_suitable_venues(self, preferences: UserPreferences, weather_data: WeatherData) -> List[Venue]:
        """Get venues that match user preferences and weather conditions"""
        
        # Build search criteria based on preferences
        criteria = SearchCriteria()
        
        # Add accessibility requirements
        if preferences.requires_accessibility():
            criteria.accessibility_required = preferences.mobility_needs
        
        # Add dietary requirements
        if preferences.dietary_restrictions:
            criteria.dietary_required = preferences.dietary_restrictions
        
        # Add budget constraints
        criteria.max_cost = preferences.budget_range[1]
        
        # Weather-based filtering
        if not weather_data.is_suitable_for_outdoor:
            criteria.weather_suitability = WeatherSuitability.INDOOR
        
        # Get all suitable venues
        venues = self.venue_service.search_venues(criteria)
        
        # Apply additional filtering
        filtered_venues = []
        for venue in venues:
            if self._is_venue_suitable(venue, preferences, weather_data):
                filtered_venues.append(venue)
        
        return filtered_venues
    
    def _is_venue_suitable(self, venue: Venue, preferences: UserPreferences, weather_data: WeatherData) -> bool:
        """Check if a venue is suitable for the user group"""
        
        # Check accessibility requirements
        if preferences.requires_accessibility():
            if 'wheelchair' in preferences.mobility_needs and not venue.accessibility.wheelchair_accessible:
                return False
            if 'elevator_only' in preferences.mobility_needs and not venue.accessibility.has_elevator:
                return False
            if 'avoid_stairs' in preferences.mobility_needs and not venue.accessibility.step_free_access:
                return False
        
        # Check dietary requirements
        if preferences.dietary_restrictions:
            if 'soft_meals' in preferences.dietary_restrictions and venue.category == VenueCategory.RESTAURANT:
                if not venue.dietary_options.soft_meals:
                    return False
            if 'vegetarian' in preferences.dietary_restrictions and venue.category == VenueCategory.RESTAURANT:
                if not venue.dietary_options.vegetarian:
                    return False
        
        # Check budget constraints
        if venue.cost_range[0] > preferences.budget_range[1]:
            return False
        
        # Check weather suitability
        if not weather_data.is_suitable_for_outdoor and venue.weather_suitability == WeatherSuitability.OUTDOOR:
            return False
        
        # Check difficulty level for seniors
        if preferences.has_seniors() and venue.accessibility.difficulty_level > 3:
            return False
        
        return True
    
    def _generate_day_plan(self, day: int, preferences: UserPreferences, weather_data: WeatherData, 
                          available_venues: List[Venue], used_venues: set) -> DayPlan:
        """Generate plan for a single day"""
        
        # Filter out already used venues
        day_venues = [v for v in available_venues if v.id not in used_venues]
        
        if not day_venues:
            # If no new venues, allow reuse but prefer unused ones
            day_venues = available_venues
        
        # Select venues for the day using AI logic
        selected_venues = self._select_daily_venues(day_venues, preferences, weather_data)
        
        # Mark venues as used
        for venue in selected_venues:
            used_venues.add(venue.id)
        
        # Generate transportation between venues
        transportation = self._generate_transportation(selected_venues, preferences)
        
        # Calculate costs and distances
        estimated_cost = self._calculate_day_cost(selected_venues, transportation, preferences)
        walking_distance = self._calculate_walking_distance(selected_venues)
        
        # Generate accessibility and weather notes
        accessibility_notes = self._generate_accessibility_notes(selected_venues, preferences)
        weather_notes = self._generate_weather_notes(weather_data)
        
        return DayPlan(
            day=day,
            venues=selected_venues,
            transportation=transportation,
            estimated_cost=estimated_cost,
            total_walking_distance=walking_distance,
            accessibility_notes=accessibility_notes,
            weather_considerations=weather_notes
        )
    
    def _select_daily_venues(self, venues: List[Venue], preferences: UserPreferences, 
                           weather_data: WeatherData) -> List[Venue]:
        """AI logic to select optimal venues for a day"""
        
        if not venues:
            return []
        
        # Categorize venues
        attractions = [v for v in venues if v.category in [VenueCategory.ATTRACTION, VenueCategory.MUSEUM, VenueCategory.PARK]]
        restaurants = [v for v in venues if v.category == VenueCategory.RESTAURANT]
        
        selected = []
        
        # Always include at least one meal
        if restaurants:
            # Prefer restaurants with senior/child discounts if applicable
            if preferences.has_seniors() or preferences.has_children():
                discounted = [r for r in restaurants if r.elderly_discount or r.child_discount]
                if discounted:
                    selected.append(random.choice(discounted))
                else:
                    selected.append(random.choice(restaurants))
            else:
                selected.append(random.choice(restaurants))
        
        # Add attractions based on weather and preferences
        remaining_slots = self.max_venues_per_day - len(selected)
        
        if attractions and remaining_slots > 0:
            # Weather-based selection
            if weather_data.is_suitable_for_outdoor:
                # Prefer outdoor venues in good weather
                outdoor_venues = [v for v in attractions if v.weather_suitability in [WeatherSuitability.OUTDOOR, WeatherSuitability.MIXED]]
                if outdoor_venues:
                    selected.extend(random.sample(outdoor_venues, min(remaining_slots, len(outdoor_venues))))
                else:
                    selected.extend(random.sample(attractions, min(remaining_slots, len(attractions))))
            else:
                # Prefer indoor venues in bad weather
                indoor_venues = [v for v in attractions if v.weather_suitability == WeatherSuitability.INDOOR]
                if indoor_venues:
                    selected.extend(random.sample(indoor_venues, min(remaining_slots, len(indoor_venues))))
                else:
                    selected.extend(random.sample(attractions, min(remaining_slots, len(attractions))))
        
        # Ensure we don't exceed max venues per day
        return selected[:self.max_venues_per_day]
    
    def _generate_transportation(self, venues: List[Venue], preferences: UserPreferences) -> List[TransportSegment]:
        """Generate transportation segments between venues"""
        transportation = []
        
        for i in range(len(venues) - 1):
            origin = venues[i].name
            destination = venues[i + 1].name
            
            # Choose transport mode based on preferences and accessibility
            if 'mtr' in preferences.transportation_preference:
                mode = 'mtr'
                duration = 20  # Average MTR journey
                cost = 15.0   # Average MTR fare
                notes = ["MTR stations are wheelchair accessible"]
            elif 'taxi' in preferences.transportation_preference:
                mode = 'taxi'
                duration = 15  # Average taxi journey
                cost = 50.0   # Average taxi fare
                notes = ["Taxi recommended for mobility needs"]
            else:
                mode = 'bus'
                duration = 25  # Average bus journey
                cost = 8.0    # Average bus fare
                notes = ["Check bus accessibility before boarding"]
            
            transportation.append(TransportSegment(
                origin=origin,
                destination=destination,
                mode=mode,
                duration_minutes=duration,
                cost=cost,
                accessibility_notes=notes
            ))
        
        return transportation
    
    def _calculate_day_cost(self, venues: List[Venue], transportation: List[TransportSegment], 
                          preferences: UserPreferences) -> float:
        """Calculate estimated cost for a day"""
        venue_costs = 0.0
        transport_costs = 0.0
        
        # Calculate venue costs
        for venue in venues:
            base_cost = (venue.cost_range[0] + venue.cost_range[1]) / 2
            
            # Apply discounts
            if preferences.has_seniors() and venue.elderly_discount:
                base_cost *= 0.8  # 20% senior discount
            if preferences.has_children() and venue.child_discount:
                base_cost *= 0.9  # 10% child discount
            
            venue_costs += base_cost * preferences.total_people()
        
        # Calculate transport costs
        for segment in transportation:
            transport_costs += segment.cost * preferences.total_people()
        
        return venue_costs + transport_costs
    
    def _calculate_walking_distance(self, venues: List[Venue]) -> float:
        """Estimate total walking distance for the day"""
        # Simplified calculation - in reality would use actual coordinates
        if len(venues) <= 1:
            return 0.0
        
        # Estimate 0.5km average walking between venues plus venue exploration
        base_distance = (len(venues) - 1) * 0.5  # Between venues
        exploration_distance = len(venues) * 0.3  # Within venues
        
        return base_distance + exploration_distance
    
    def _generate_accessibility_notes(self, venues: List[Venue], preferences: UserPreferences) -> List[str]:
        """Generate accessibility notes for the day"""
        notes = []
        
        if preferences.requires_accessibility():
            wheelchair_venues = sum(1 for v in venues if v.accessibility.wheelchair_accessible)
            elevator_venues = sum(1 for v in venues if v.accessibility.has_elevator)
            
            notes.append(f"{wheelchair_venues}/{len(venues)} venues are wheelchair accessible")
            notes.append(f"{elevator_venues}/{len(venues)} venues have elevators")
            
            if any('rest_frequent' in preferences.mobility_needs for _ in [1]):
                rest_venues = sum(1 for v in venues if v.accessibility.rest_areas)
                notes.append(f"{rest_venues}/{len(venues)} venues have rest areas")
        
        return notes
    
    def _generate_weather_notes(self, weather_data: WeatherData) -> List[str]:
        """Generate weather-related notes"""
        notes = []
        
        if weather_data.rainfall_probability > 50:
            notes.append("High chance of rain - indoor activities recommended")
        
        if weather_data.temperature > 30:
            notes.append("Hot weather - stay hydrated and take breaks in air conditioning")
        elif weather_data.temperature < 18:
            notes.append("Cool weather - dress warmly for outdoor activities")
        
        if weather_data.humidity > 80:
            notes.append("High humidity - take frequent breaks")
        
        return notes
    
    def _calculate_total_cost(self, day_plans: List[DayPlan], preferences: UserPreferences) -> Tuple[float, CostBreakdown]:
        """Calculate total trip cost and breakdown"""
        total_attractions = 0.0
        total_meals = 0.0
        total_transport = 0.0
        
        for day_plan in day_plans:
            for venue in day_plan.venues:
                avg_cost = (venue.cost_range[0] + venue.cost_range[1]) / 2 * preferences.total_people()
                
                if venue.category == VenueCategory.RESTAURANT:
                    total_meals += avg_cost
                else:
                    total_attractions += avg_cost
            
            for transport in day_plan.transportation:
                total_transport += transport.cost * preferences.total_people()
        
        total = total_attractions + total_meals + total_transport
        
        cost_breakdown = CostBreakdown(
            attractions=total_attractions,
            meals=total_meals,
            transportation=total_transport,
            total=total,
            cost_per_person=total / preferences.total_people()
        )
        
        return total, cost_breakdown
    
    def _calculate_accessibility_score(self, day_plans: List[DayPlan], preferences: UserPreferences) -> float:
        """Calculate overall accessibility score (1-5)"""
        if not preferences.requires_accessibility():
            return 5.0  # Perfect score if no accessibility needs
        
        total_venues = sum(len(day.venues) for day in day_plans)
        if total_venues == 0:
            return 1.0
        
        accessibility_points = 0
        max_points = total_venues * 5  # 5 points per venue max
        
        for day_plan in day_plans:
            for venue in day_plan.venues:
                points = 0
                if venue.accessibility.wheelchair_accessible:
                    points += 1
                if venue.accessibility.has_elevator:
                    points += 1
                if venue.accessibility.accessible_toilets:
                    points += 1
                if venue.accessibility.step_free_access:
                    points += 1
                if venue.accessibility.rest_areas:
                    points += 1
                
                accessibility_points += points
        
        # Convert to 1-5 scale
        score = (accessibility_points / max_points) * 5
        return round(score, 1)