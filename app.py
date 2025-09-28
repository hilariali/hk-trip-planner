"""
Hong Kong Trip Planner - AI-Powered Accessible Itinerary Generator
Main Streamlit application for families and seniors visiting Hong Kong
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import json

# Import our custom modules
from models import Venue, UserPreferences, Itinerary, AccessibilityInfo, DayPlan
from services.venue_service import VenueService
from services.weather_service import WeatherService
from services.itinerary_engine import ItineraryEngine

# Page configuration
st.set_page_config(
    page_title="Hong Kong Trip Planner",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application entry point"""
    st.title("🏙️ Hong Kong Trip Planner")
    st.markdown("### AI-Powered Accessible Itineraries for Families & Seniors")
    
    # Initialize services
    if 'venue_service' not in st.session_state:
        st.session_state.venue_service = VenueService()
    
    if 'weather_service' not in st.session_state:
        st.session_state.weather_service = WeatherService()
    
    if 'itinerary_engine' not in st.session_state:
        st.session_state.itinerary_engine = ItineraryEngine()
    
    # Sidebar for user preferences
    with st.sidebar:
        st.header("Trip Preferences")
        user_preferences = collect_user_preferences()
    
    # Main content area
    if user_preferences:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Generate Itinerary", type="primary", use_container_width=True):
                with st.spinner("Creating your accessible Hong Kong itinerary..."):
                    itinerary = generate_itinerary(user_preferences)
                    if itinerary:
                        display_itinerary(itinerary)
        
        with col2:
            st.info("💡 **Accessibility Focus**\n\nAll recommendations include:\n- Elevator/stair information\n- Accessible toilets\n- Soft meal options\n- Rest areas\n- Budget-friendly options")

def collect_user_preferences() -> Optional[UserPreferences]:
    """Collect user preferences through Streamlit form"""
    with st.form("preferences_form"):
        st.subheader("Family Composition")
        
        # Family composition
        adults = st.number_input("Adults", min_value=1, max_value=10, value=2)
        children = st.number_input("Children (under 12)", min_value=0, max_value=10, value=0)
        seniors = st.number_input("Seniors (65+)", min_value=0, max_value=10, value=0)
        
        st.subheader("Accessibility Needs")
        
        # Mobility requirements
        mobility_needs = st.multiselect(
            "Mobility Requirements",
            ["wheelchair", "elevator_only", "avoid_stairs", "walking_aid", "rest_frequent"],
            help="Select all that apply to your group"
        )
        
        # Dietary restrictions
        dietary_restrictions = st.multiselect(
            "Dietary Preferences",
            ["soft_meals", "vegetarian", "halal", "no_seafood", "allergies"],
            help="Select dietary requirements for your group"
        )
        
        st.subheader("Trip Details")
        
        # Budget range
        budget_min, budget_max = st.slider(
            "Budget per person per day (HKD)",
            min_value=100, max_value=2000, value=(300, 800),
            help="Includes meals, attractions, and local transport"
        )
        
        # Trip duration
        trip_duration = st.number_input(
            "Trip duration (days)", 
            min_value=1, max_value=14, value=3
        )
        
        # Transportation preferences
        transport_prefs = st.multiselect(
            "Preferred Transportation",
            ["mtr", "bus", "taxi", "walking"],
            default=["mtr", "taxi"],
            help="MTR is most accessible for wheelchairs"
        )
        
        submitted = st.form_submit_button("Set Preferences")
        
        if submitted:
            return UserPreferences(
                family_composition={"adults": adults, "children": children, "seniors": seniors},
                mobility_needs=mobility_needs,
                dietary_restrictions=dietary_restrictions,
                budget_range=(budget_min, budget_max),
                trip_duration=trip_duration,
                transportation_preference=transport_prefs
            )
    
    return None

def generate_itinerary(preferences: UserPreferences) -> Optional[Itinerary]:
    """Generate itinerary based on user preferences"""
    try:
        # Get current weather
        weather_data = st.session_state.weather_service.get_current_weather()
        
        # Generate itinerary using AI engine
        itinerary = st.session_state.itinerary_engine.generate_itinerary(
            preferences, weather_data
        )
        
        return itinerary
    except Exception as e:
        st.error(f"Error generating itinerary: {str(e)}")
        return None

def display_itinerary(itinerary: Itinerary):
    """Display the generated itinerary"""
    st.success("✅ Your accessible Hong Kong itinerary is ready!")
    
    # Display summary
    st.subheader("Trip Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Days", len(itinerary.day_plans))
    with col2:
        st.metric("Estimated Cost", f"HKD {itinerary.total_cost:.0f}")
    with col3:
        st.metric("Accessibility Score", f"{itinerary.accessibility_score}/5")
    
    # Display day-by-day plans
    for day_plan in itinerary.day_plans:
        display_day_plan(day_plan)
    
    # Export options
    st.subheader("Export Your Itinerary")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = export_to_csv(itinerary)
        st.download_button(
            "📄 Download CSV",
            csv_data,
            file_name=f"hk_itinerary_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        json_data = export_to_json(itinerary)
        st.download_button(
            "📋 Download JSON",
            json_data,
            file_name=f"hk_itinerary_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

def display_day_plan(day_plan: DayPlan):
    """Display a single day's plan"""
    with st.expander(f"Day {day_plan.day} - {len(day_plan.venues)} stops"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            for i, venue in enumerate(day_plan.venues):
                st.markdown(f"**{i+1}. {venue.name}**")
                st.markdown(f"📍 {venue.category.value}")
                
                # Accessibility info
                acc_info = []
                if venue.accessibility.wheelchair_accessible:
                    acc_info.append("♿ Wheelchair accessible")
                if venue.accessibility.has_elevator:
                    acc_info.append("🛗 Elevator available")
                if venue.accessibility.accessible_toilets:
                    acc_info.append("🚻 Accessible toilets")
                
                if acc_info:
                    st.markdown("✅ " + " • ".join(acc_info))
                
                st.markdown(f"💰 HKD {venue.cost_range[0]}-{venue.cost_range[1]}")
                st.markdown("---")
        
        with col2:
            st.metric("Day Cost", f"HKD {day_plan.estimated_cost:.0f}")
            st.metric("Walking", f"{day_plan.total_walking_distance:.1f}km")

def export_to_csv(itinerary: Itinerary) -> str:
    """Export itinerary to CSV format"""
    rows = []
    for day_plan in itinerary.day_plans:
        for venue in day_plan.venues:
            rows.append({
                'Day': day_plan.day,
                'Venue': venue.name,
                'Category': venue.category.value,
                'Cost_Min': venue.cost_range[0],
                'Cost_Max': venue.cost_range[1],
                'Wheelchair_Accessible': venue.accessibility.wheelchair_accessible,
                'Has_Elevator': venue.accessibility.has_elevator,
                'Accessible_Toilets': venue.accessibility.accessible_toilets
            })
    
    df = pd.DataFrame(rows)
    return df.to_csv(index=False)

def export_to_json(itinerary: Itinerary) -> str:
    """Export itinerary to JSON format"""
    return json.dumps(asdict(itinerary), indent=2, default=str)

if __name__ == "__main__":
    main()