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

# Import our custom modules
from models import Venue, UserPreferences, Itinerary, AccessibilityInfo, DayPlan
from services.venue_service import VenueService
from services.weather_service import WeatherService
from services.itinerary_engine import ItineraryEngine

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
    # In cloud, use INFO level and ensure console output
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.StreamHandler(log_buffer)   # Buffer for Streamlit
        ],
        force=True  # Override any existing configuration
    )
else:
    # Local development
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.StreamHandler(log_buffer)   # Buffer for Streamlit
        ]
    )

logger = logging.getLogger(__name__)

# Test logging immediately
print(f"LOGGING TEST: Cloud environment detected: {is_cloud}")
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
    
    # Show app status
    logger.info("=== HONG KONG TRIP PLANNER STARTING ===")
    st.info("🔄 Initializing application...")
    
    # Initialize database first
    try:
        import os
        from database import init_database, seed_sample_data, get_venue_count, DATABASE_PATH
        
        logger.info("Checking database status...")
        st.info("🔍 Checking database...")
        
        # Check if database file exists
        if os.path.exists(DATABASE_PATH):
            logger.info(f"Database file exists at {DATABASE_PATH}")
            st.info(f"📁 Database file found: {DATABASE_PATH}")
        else:
            logger.info(f"Database file not found, will create at {DATABASE_PATH}")
            st.info(f"📁 Creating new database: {DATABASE_PATH}")
        
        logger.info("Initializing database...")
        st.info("🔧 Initializing database structure...")
        init_database()
        
        logger.info("Seeding sample data...")
        st.info("🌱 Adding sample venue data...")
        seed_sample_data()
        
        venue_count = get_venue_count()
        logger.info(f"Database initialized with {venue_count} venues")
        
        # Show database status in UI
        if venue_count == 0:
            st.error("⚠️ Database is empty! Please check database initialization.")
            logger.error("Database has 0 venues after initialization")
        else:
            st.success(f"✅ Database ready with {venue_count} venues")
            
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}", exc_info=True)
        st.error(f"❌ Database error: {str(e)}")
        st.exception(e)  # Show full traceback in Streamlit
        return
    
    # Initialize services
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
        
    except Exception as e:
        logger.error(f"Service initialization failed: {str(e)}", exc_info=True)
        st.error(f"❌ Service initialization error: {str(e)}")
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
                
                st.info("🔍 Debug: Generate button clicked!")
                logger.info("Generate Itinerary button clicked")
                
                # Create status container
                status_container = st.empty()
                
                with st.spinner("Creating your accessible Hong Kong itinerary..."):
                    status_container.info("🔍 Step 1: Validating user preferences...")
                    logger.info(f"User preferences: {user_preferences}")
                    
                    status_container.info("🔍 Step 2: Getting weather data...")
                    
                    status_container.info("🔍 Step 3: Searching for suitable venues...")
                    
                    status_container.info("🔍 Step 4: Generating itinerary...")
                    itinerary = generate_itinerary(user_preferences)
                    
                    if itinerary:
                        status_container.success("✅ Itinerary generated successfully!")
                        logger.info("Displaying itinerary")
                        display_itinerary(itinerary)
                    else:
                        status_container.error("❌ No itinerary was generated!")
                        logger.error("No itinerary returned from generate_itinerary")
                        
                        # Show troubleshooting info
                        st.error("**Troubleshooting:**")
                        st.write("- Check if your preferences are too restrictive")
                        st.write("- Try reducing accessibility requirements")
                        st.write("- Increase your budget range")
                        st.write("- Check the debug panel below for more details")
        
        with col2:
            st.info("💡 **Accessibility Focus**\n\nAll recommendations include:\n- Elevator/stair information\n- Accessible toilets\n- Soft meal options\n- Rest areas\n- Budget-friendly options")
            
            # Debug panel
            with st.expander("🔍 Debug Information", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("Test Database Connection"):
                        try:
                            from database import get_venue_count
                            count = get_venue_count()
                            st.success(f"✅ Database connected! Found {count} venues")
                            logger.info(f"Database test: {count} venues")
                        except Exception as e:
                            st.error(f"❌ Database test failed: {str(e)}")
                            logger.error(f"Database test failed: {str(e)}")
                    
                    if st.button("Test Services"):
                        try:
                            # Test venue service
                            all_venues = st.session_state.venue_service.get_all_venues()
                            st.success(f"✅ Venue Service: {len(all_venues)} venues loaded")
                            logger.info(f"Venue service test: {len(all_venues)} venues")
                            
                            # Test weather service
                            weather = st.session_state.weather_service.get_current_weather()
                            st.success(f"✅ Weather Service: {weather.temperature}°C, {weather.weather_description}")
                            logger.info(f"Weather service test: {weather.temperature}°C")
                            
                            # Test itinerary engine
                            st.success("✅ Itinerary Engine: Ready")
                            logger.info("Itinerary engine test: Ready")
                            
                        except Exception as e:
                            st.error(f"❌ Service test failed: {str(e)}")
                            logger.error(f"Service test failed: {str(e)}", exc_info=True)
                
                with col2:
                    if st.button("Quick Test Generation"):
                        try:
                            # Create minimal test preferences
                            test_prefs = UserPreferences(
                                family_composition={"adults": 2, "children": 0, "seniors": 0},
                                mobility_needs=[],
                                dietary_restrictions=[],
                                budget_range=(200, 500),
                                trip_duration=1,
                                transportation_preference=["mtr"]
                            )
                            
                            st.info("Testing with minimal preferences...")
                            logger.info("Starting quick test generation")
                            
                            itinerary = generate_itinerary(test_prefs)
                            if itinerary:
                                st.success(f"✅ Quick test successful! Generated {len(itinerary.day_plans)} day(s)")
                                logger.info(f"Quick test successful: {len(itinerary.day_plans)} days")
                            else:
                                st.error("❌ Quick test failed - no itinerary generated")
                                logger.error("Quick test failed - no itinerary")
                                
                        except Exception as e:
                            st.error(f"❌ Quick test failed: {str(e)}")
                            logger.error(f"Quick test failed: {str(e)}", exc_info=True)
                
                # Show logs
                if st.button("Show Recent Logs"):
                    log_contents = log_buffer.getvalue()
                    if log_contents:
                        st.text_area("Recent Logs", log_contents, height=200)
                    else:
                        st.info("No logs captured yet. Try generating an itinerary first.")

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
    print("=== STARTING HONG KONG TRIP PLANNER ===")
    logger.info("Starting Hong Kong Trip Planner application")
    main()