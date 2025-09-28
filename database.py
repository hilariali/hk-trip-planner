"""
Database setup and management for Hong Kong Trip Planner
SQLite database initialization and schema creation
"""

import sqlite3
import os
from typing import List, Dict, Any
from contextlib import contextmanager

DATABASE_PATH = "hk_trip_planner.db"

def init_database():
    """Initialize the SQLite database with required tables"""
    with sqlite3.connect(DATABASE_PATH) as conn:
        cursor = conn.cursor()
        
        # Create venues table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS venues (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                address TEXT,
                district TEXT,
                has_elevator BOOLEAN DEFAULT 0,
                wheelchair_accessible BOOLEAN DEFAULT 0,
                accessible_toilets BOOLEAN DEFAULT 0,
                step_free_access BOOLEAN DEFAULT 0,
                parent_facilities BOOLEAN DEFAULT 0,
                rest_areas BOOLEAN DEFAULT 0,
                difficulty_level INTEGER DEFAULT 1,
                soft_meals_available BOOLEAN DEFAULT 0,
                vegetarian_options BOOLEAN DEFAULT 0,
                halal_options BOOLEAN DEFAULT 0,
                no_seafood_options BOOLEAN DEFAULT 0,
                allergy_friendly BOOLEAN DEFAULT 0,
                cost_min INTEGER,
                cost_max INTEGER,
                weather_suitability TEXT DEFAULT 'mixed',
                description TEXT,
                phone TEXT,
                website TEXT,
                elderly_discount BOOLEAN DEFAULT 0,
                child_discount BOOLEAN DEFAULT 0,
                opening_hours TEXT,
                accessibility_notes TEXT,
                dietary_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create user sessions table for temporary storage
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                preferences TEXT,
                generated_itinerary TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_venues_category ON venues(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_venues_district ON venues(district)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_venues_accessibility ON venues(wheelchair_accessible, has_elevator)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_venues_cost ON venues(cost_min, cost_max)")
        
        conn.commit()

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    try:
        yield conn
    finally:
        conn.close()

def seed_sample_data():
    """Seed the database with sample Hong Kong venues"""
    sample_venues = [
        # Attractions
        {
            'id': 'hk_001',
            'name': 'Victoria Peak Sky Terrace',
            'category': 'attraction',
            'latitude': 22.2711,
            'longitude': 114.1489,
            'address': 'The Peak, Hong Kong Island',
            'district': 'Central and Western',
            'has_elevator': 1,
            'wheelchair_accessible': 1,
            'accessible_toilets': 1,
            'step_free_access': 0,  # Peak Tram has steps
            'parent_facilities': 1,
            'rest_areas': 1,
            'difficulty_level': 3,
            'cost_min': 65,
            'cost_max': 99,
            'weather_suitability': 'outdoor',
            'description': 'Iconic Hong Kong skyline views from the highest point',
            'elderly_discount': 1,
            'child_discount': 1,
            'opening_hours': '{"monday": "10:00-23:00", "sunday": "10:00-23:00"}',
            'accessibility_notes': 'Peak Tram accessible, but has some steps. Sky Terrace fully accessible.',
            'dietary_notes': '',
            'soft_meals_available': 0,
            'vegetarian_options': 0,
            'halal_options': 0,
            'no_seafood_options': 0,
            'allergy_friendly': 0
        },
        {
            'id': 'hk_002', 
            'name': 'Hong Kong Space Museum',
            'category': 'museum',
            'latitude': 22.2942,
            'longitude': 114.1722,
            'address': '10 Salisbury Road, Tsim Sha Tsui',
            'district': 'Yau Tsim Mong',
            'has_elevator': 1,
            'wheelchair_accessible': 1,
            'accessible_toilets': 1,
            'step_free_access': 1,
            'parent_facilities': 1,
            'rest_areas': 1,
            'difficulty_level': 1,
            'cost_min': 10,
            'cost_max': 32,
            'weather_suitability': 'indoor',
            'description': 'Interactive space and astronomy exhibits, perfect for families',
            'elderly_discount': 1,
            'child_discount': 1,
            'opening_hours': '{"monday": "closed", "tuesday": "10:00-21:00", "sunday": "10:00-21:00"}',
            'accessibility_notes': 'Full wheelchair access, tactile exhibits available',
            'dietary_notes': '',
            'soft_meals_available': 0,
            'vegetarian_options': 0,
            'halal_options': 0,
            'no_seafood_options': 0,
            'allergy_friendly': 0
        },
        {
            'id': 'hk_003',
            'name': 'Hong Kong Park',
            'category': 'park',
            'latitude': 22.2769,
            'longitude': 114.1628,
            'address': '19 Cotton Tree Drive, Central',
            'district': 'Central and Western',
            'has_elevator': 0,
            'wheelchair_accessible': 1,
            'accessible_toilets': 1,
            'step_free_access': 1,
            'parent_facilities': 1,
            'rest_areas': 1,
            'difficulty_level': 1,
            'cost_min': 0,
            'cost_max': 0,
            'weather_suitability': 'outdoor',
            'description': 'Beautiful urban park with aviary and tai chi garden',
            'elderly_discount': 0,
            'child_discount': 0,
            'opening_hours': '{"monday": "06:00-23:00", "sunday": "06:00-23:00"}',
            'accessibility_notes': 'Paved paths, accessible restrooms available',
            'dietary_notes': '',
            'soft_meals_available': 0,
            'vegetarian_options': 0,
            'halal_options': 0,
            'no_seafood_options': 0,
            'allergy_friendly': 0
        },
        
        # Restaurants
        {
            'id': 'hk_r001',
            'name': 'Maxim\'s Palace Dim Sum',
            'category': 'restaurant',
            'latitude': 22.2942,
            'longitude': 114.1722,
            'address': 'Shop 2-5, 2/F, Low Block, City Hall, Central',
            'district': 'Central and Western',
            'has_elevator': 1,
            'wheelchair_accessible': 1,
            'accessible_toilets': 1,
            'step_free_access': 1,
            'parent_facilities': 1,
            'rest_areas': 0,
            'difficulty_level': 1,
            'soft_meals_available': 1,
            'vegetarian_options': 1,
            'halal_options': 0,
            'no_seafood_options': 0,
            'allergy_friendly': 0,
            'cost_min': 150,
            'cost_max': 300,
            'weather_suitability': 'indoor',
            'description': 'Traditional dim sum restaurant with soft, senior-friendly options',
            'elderly_discount': 0,
            'child_discount': 0,
            'opening_hours': '{"monday": "11:00-15:00", "sunday": "10:00-16:00"}',
            'accessibility_notes': 'Elevator access, wide aisles for wheelchairs',
            'dietary_notes': 'Steamed dim sum perfect for seniors, vegetarian options available'
        },
        {
            'id': 'hk_r002',
            'name': 'Café de Coral (Accessible Branch)',
            'category': 'restaurant',
            'latitude': 22.2783,
            'longitude': 114.1747,
            'address': 'Multiple locations - Admiralty Centre',
            'district': 'Central and Western',
            'has_elevator': 1,
            'wheelchair_accessible': 1,
            'accessible_toilets': 1,
            'step_free_access': 1,
            'parent_facilities': 1,
            'rest_areas': 0,
            'difficulty_level': 1,
            'soft_meals_available': 1,
            'vegetarian_options': 1,
            'halal_options': 0,
            'no_seafood_options': 1,
            'allergy_friendly': 0,
            'cost_min': 50,
            'cost_max': 120,
            'weather_suitability': 'indoor',
            'description': 'Local fast food chain with soft congee and soup options',
            'elderly_discount': 0,
            'child_discount': 0,
            'opening_hours': '{"monday": "07:00-22:00", "sunday": "07:00-22:00"}',
            'accessibility_notes': 'Ground floor access, wide entrance',
            'dietary_notes': 'Congee, steamed fish, soft vegetables available'
        },
        
        # Transport hubs
        {
            'id': 'hk_t001',
            'name': 'Central MTR Station',
            'category': 'transport',
            'latitude': 22.2816,
            'longitude': 114.1578,
            'address': 'Central, Hong Kong Island',
            'district': 'Central and Western',
            'has_elevator': 1,
            'wheelchair_accessible': 1,
            'accessible_toilets': 1,
            'step_free_access': 1,
            'parent_facilities': 1,
            'rest_areas': 1,
            'difficulty_level': 1,
            'cost_min': 0,
            'cost_max': 0,
            'weather_suitability': 'indoor',
            'description': 'Major MTR interchange with full accessibility features',
            'elderly_discount': 0,
            'child_discount': 0,
            'opening_hours': '{"monday": "05:30-01:00", "sunday": "05:30-01:00"}',
            'accessibility_notes': 'Full accessibility features, tactile guidance systems',
            'dietary_notes': '',
            'soft_meals_available': 0,
            'vegetarian_options': 0,
            'halal_options': 0,
            'no_seafood_options': 0,
            'allergy_friendly': 0
        }
    ]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for venue in sample_venues:
            cursor.execute("""
                INSERT OR REPLACE INTO venues (
                    id, name, category, latitude, longitude, address, district,
                    has_elevator, wheelchair_accessible, accessible_toilets, 
                    step_free_access, parent_facilities, rest_areas, difficulty_level,
                    soft_meals_available, vegetarian_options, halal_options,
                    cost_min, cost_max, weather_suitability, description,
                    elderly_discount, child_discount, opening_hours, 
                    accessibility_notes, dietary_notes
                ) VALUES (
                    :id, :name, :category, :latitude, :longitude, :address, :district,
                    :has_elevator, :wheelchair_accessible, :accessible_toilets,
                    :step_free_access, :parent_facilities, :rest_areas, :difficulty_level,
                    :soft_meals_available, :vegetarian_options, :halal_options,
                    :cost_min, :cost_max, :weather_suitability, :description,
                    :elderly_discount, :child_discount, :opening_hours,
                    :accessibility_notes, :dietary_notes
                )
            """, venue)
        
        conn.commit()

def get_venue_count() -> int:
    """Get total number of venues in database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM venues")
        return cursor.fetchone()[0]

if __name__ == "__main__":
    # Initialize database and seed with sample data
    init_database()
    seed_sample_data()
    print(f"Database initialized with {get_venue_count()} venues")