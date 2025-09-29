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
import logging

# Import our custom modules with error handling
try:
    from models import Venue, UserPreferences, Itinerary, AccessibilityInfo, DayPlan
    from services.venue_service import VenueService
    from services.weather_service import WeatherService
    from services.itinerary_engine import ItineraryEngine
except ImportError as e:
    import sys
    print(f"Import error: {e}")
    print("Please ensure all required modules are available")
    sys.exit(1)

# Configure logging with in-memory handler for Streamlit
import io
import sys
import os

# Create a string buffer to capture logs
log_buffer = io.StringIO()

# Check if we're in a cloud environment
is_cloud = os.getenv('STREAMLIT_SHARING') or os.getenv('HEROKU') or '/mount/src' in os.getcwd()

# Configure logging
if is_cloud:
    # In cloud, use WARNING level to reduce noise
    logging.basicConfig(
        level=logging.WARNING, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.StreamHandler(log_buffer)   # Buffer for Streamlit
        ],
        force=True  # Override any existing configuration
    )
else:
    # Local development - more verbose
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.StreamHandler(log_buffer)   # Buffer for Streamlit
        ]
    )

logger = logging.getLogger('app')

# Only log in development
if not is_cloud:
    logger.info(f"Logger initialized - Cloud environment: {is_cloud}")

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
    
    # Initialize application silently
    logger.info("=== HONG KONG TRIP PLANNER STARTING ===")
    
    # Initialize database first
    try:
        import os
        from database import init_database, seed_sample_data, get_venue_count, DATABASE_PATH
        
        logger.info("Checking database status...")
        
        # Check if database file exists
        if os.path.exists(DATABASE_PATH):
            logger.info(f"Database file exists at {DATABASE_PATH}")
        else:
            logger.info(f"Database file not found, will create at {DATABASE_PATH}")
        
        logger.info("Initializing database...")
        init_database()
        
        logger.info("Seeding sample data...")
        seed_sample_data()
        
        venue_count = get_venue_count()
        logger.info(f"Database initialized with {venue_count} venues")
        
        # Only show error if database is empty
        if venue_count == 0:
            st.error("⚠️ Application data is not available. Please try refreshing the page.")
            logger.error("Database has 0 venues after initialization")
            return
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        st.error("⚠️ Application is temporarily unavailable. Please try refreshing the page.")
        return
    
    # Initialize services with error handling
    try:
        if 'venue_service' not in st.session_state:
            logger.info("Initializing venue service...")
            st.session_state.venue_service = VenueService()
        
        if 'weather_service' not in st.session_state:
            logger.info("Initializing weather service...")
            st.session_state.weather_service = WeatherService()
        
        if 'itinerary_engine' not in st.session_state:
            logger.info("Initializing itinerary engine...")
            st.session_state.itinerary_engine = ItineraryEngine()
            
        logger.info("All services initialized successfully")
        
        # Test if government APIs are available (do this quietly)
        try:
            test_venues = st.session_state.venue_service.get_all_venues()
            if len(test_venues) > 6:  # More than just local venues
                logger.info("Government APIs are working")
            else:
                logger.info("Using local venue database only")
        except Exception as api_e:
            logger.warning(f"Government APIs not available: {api_e}")
        
    except Exception as e:
        logger.error(f"Service initialization failed: {str(e)}", exc_info=True)
        st.error("⚠️ Application services are temporarily unavailable. Please try refreshing the page.")
        return
    
    # Sidebar for user preferences
    with st.sidebar:
        st.header("Trip Preferences")
        user_preferences = collect_user_preferences()
    
    # Main content area
    if user_preferences:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("Generate Itinerary", type="primary", use_container_width=True):
                # Clear previous logs
                log_buffer.seek(0)
                log_buffer.truncate(0)
                
                logger.info("Generate Itinerary button clicked")
                logger.info(f"User preferences: {user_preferences}")
                
                # Create status container for user-friendly messages
                status_container = st.empty()
                
                with st.spinner("Creating your accessible Hong Kong itinerary..."):
                    status_container.info("🔍 Analyzing your preferences...")
                    
                    status_container.info("🌤️ Checking current weather conditions...")
                    
                    status_container.info("🏛️ Finding suitable venues and attractions...")
                    
                    status_container.info("📋 Building your personalized itinerary...")
                    
                    itinerary = generate_itinerary(user_preferences)
                    
                    if itinerary:
                        status_container.success("✅ Your itinerary is ready!")
                        logger.info("Displaying itinerary")
                        display_itinerary(itinerary)
                    else:
                        status_container.empty()
                        logger.error("No itinerary returned from generate_itinerary")
                        
                        # Show user-friendly no results message
                        st.warning("🤔 **No suitable itinerary found**")
                        st.markdown("""
                        We couldn't find venues that match all your requirements. Try adjusting:
                        
                        **💡 Suggestions:**
                        - **Budget**: Increase your daily budget range
                        - **Accessibility**: Reduce specific mobility requirements if flexible
                        - **Dietary**: Remove dietary restrictions if not essential
                        - **Duration**: Try a shorter trip duration
                        
                        **🎯 Quick Fix:** Try removing some filters and generate again!
                        """)
                        
                        # Add a quick retry button with relaxed preferences
                        if st.button("🔄 Try with Relaxed Preferences", type="secondary"):
                            relaxed_prefs = UserPreferences(
                                family_composition=user_preferences.family_composition,
                                mobility_needs=[],  # Remove mobility restrictions
                                dietary_restrictions=[],  # Remove dietary restrictions
                                budget_range=(200, 1000),  # Wider budget range
                                trip_duration=min(user_preferences.trip_duration, 2),  # Shorter duration
                                transportation_preference=user_preferences.transportation_preference
                            )
                            
                            with st.spinner("Trying with more flexible preferences..."):
                                relaxed_itinerary = generate_itinerary(relaxed_prefs)
                                if relaxed_itinerary:
                                    st.success("✅ Found an itinerary with relaxed preferences!")
                                    display_itinerary(relaxed_itinerary)
                                else:
                                    st.error("❌ Still no results. Please contact support.")
        
        with col2:
            st.info("💡 **Accessibility Focus**\n\nAll recommendations include:\n- Elevator/stair information\n- Accessible toilets\n- Soft meal options\n- Rest areas\n- Budget-friendly options\n- Real-time weather data")
            
            # Tips for better results
            with st.expander("💡 Tips for Better Results"):
                st.markdown("""
                **🎯 Getting Great Itineraries:**
                - **Budget**: HKD 300-800 per person works best
                - **Duration**: 1-3 days for first-time visitors
                - **Flexibility**: Fewer restrictions = more options
                
                **♿ Accessibility Notes:**
                - MTR stations are wheelchair accessible
                - Most major attractions have elevators
                - Restaurants can accommodate dietary needs
                
                **🌟 Popular Combinations:**
                - Families: Parks + Museums + Dim Sum
                - Seniors: Indoor attractions + Accessible transport
                - Budget travelers: Free parks + Local eateries
                """)
            
            # Data sources information
            with st.expander("📊 Official Data Sources"):
                st.markdown("""
                **🏛️ Government APIs Used:**
                - **HK Tourism Board**: Major attractions & events
                - **HK Observatory**: Real-time weather & forecasts
                - **MTR Corporation**: Accessibility facilities
                - **FEHD**: Licensed restaurant database
                - **Rehabilitation Society**: Accessible facilities
                - **Lands Department**: Geographic data
                
                **🔄 Data Updates:**
                - Weather: Real-time
                - Attractions: Daily
                - Events: Weekly
                - Facilities: Monthly
                
                **📍 Coverage:**
                - 18 Districts of Hong Kong
                - 1000+ Venues & Attractions
                - 500+ Accessibility Points
                - Real-time Transport Info
                """)
            
            # Hidden debug panel (only show if there are issues)
            if st.session_state.get('show_debug', False):
                with st.expander("🔧 Technical Support", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("Test Database"):
                            try:
                                from database import get_venue_count
                                count = get_venue_count()
                                st.success(f"✅ Database: {count} venues")
                                logger.info(f"Database test: {count} venues")
                            except Exception as e:
                                st.error(f"❌ Database error: {str(e)}")
                                logger.error(f"Database test failed: {str(e)}")
                        
                        if st.button("Test Services"):
                            try:
                                all_venues = st.session_state.venue_service.get_all_venues()
                                weather = st.session_state.weather_service.get_current_weather()
                                st.success(f"✅ Services: {len(all_venues)} venues, {weather.temperature}°C")
                                logger.info(f"Services test: {len(all_venues)} venues, {weather.temperature}°C")
                            except Exception as e:
                                st.error(f"❌ Services error: {str(e)}")
                                logger.error(f"Services test failed: {str(e)}", exc_info=True)
                    
                    with col2:
                        if st.button("Show Logs"):
                            log_contents = log_buffer.getvalue()
                            if log_contents:
                                st.text_area("Recent Logs", log_contents, height=150)
                            else:
                                st.info("No recent logs available.")
            
            # Show debug panel if user encounters issues
            if not st.session_state.get('show_debug', False):
                if st.button("🔧 Having Issues? Click for Technical Support", key="debug_toggle"):
                    st.session_state.show_debug = True
                    st.experimental_rerun()

def collect_user_preferences() -> Optional[UserPreferences]:
    """Collect user preferences through Streamlit form"""
    logger.info("Rendering user preferences form")
    
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
        logger.info("=== STARTING ITINERARY GENERATION ===")
        logger.info(f"User preferences: {preferences}")
        
        # Get current weather
        logger.info("Getting weather data...")
        weather_data = st.session_state.weather_service.get_current_weather()
        logger.info(f"Weather data: {weather_data}")
        
        # Generate itinerary using AI engine
        logger.info("Calling itinerary engine...")
        itinerary = st.session_state.itinerary_engine.generate_itinerary(
            preferences, weather_data
        )
        
        if itinerary:
            logger.info(f"Successfully generated itinerary with {len(itinerary.day_plans)} days")
            logger.info(f"Total cost: {itinerary.total_cost}")
        else:
            logger.warning("Itinerary generation returned None")
        
        return itinerary
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}", exc_info=True)
        # Don't show technical error to user, just log it
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
    if not is_cloud:
        print("=== STARTING HONG KONG TRIP PLANNER ===")
        logger.info("Starting Hong Kong Trip Planner application")
    main()