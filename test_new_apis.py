#!/usr/bin/env python3
"""
Test script for new Hong Kong government API endpoints
"""

import requests
import csv
import io
import xml.etree.ElementTree as ET
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('test_new_apis')

def test_hk_tourism_attractions():
    """Test HK Tourism Board attractions CSV"""
    logger.info("Testing HK Tourism Board attractions CSV...")
    
    try:
        url = "https://www.tourism.gov.hk/datagovhk/major_attractions/major_attractions_info_en.csv"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            reader = csv.DictReader(io.StringIO(response.text))
            attractions = list(reader)
            logger.info(f"✅ Successfully fetched {len(attractions)} attractions from CSV")
            
            # Show sample data
            if attractions:
                sample = attractions[0]
                logger.info(f"Sample attraction: {sample.get('Name (English)', 'N/A')}")
                logger.info(f"Available fields: {list(sample.keys())}")
            
            return True
        else:
            logger.error(f"❌ CSV API returned status {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error fetching attractions CSV: {str(e)}")
        return False

def test_hk_weather_apis():
    """Test HK Observatory weather APIs"""
    logger.info("Testing HK Observatory weather APIs...")
    
    # Test current weather
    try:
        current_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en"
        response = requests.get(current_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Successfully fetched current weather data")
            logger.info(f"Available fields: {list(data.keys())}")
        else:
            logger.error(f"❌ Current weather API returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error fetching current weather: {str(e)}")
    
    # Test forecast
    try:
        forecast_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=en"
        response = requests.get(forecast_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Successfully fetched weather forecast data")
            if 'weatherForecast' in data:
                logger.info(f"Forecast days available: {len(data['weatherForecast'])}")
        else:
            logger.error(f"❌ Forecast API returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error fetching weather forecast: {str(e)}")

def test_mtr_apis():
    """Test MTR CSV APIs"""
    logger.info("Testing MTR CSV APIs...")
    
    # Test stations
    try:
        stations_url = "https://opendata.mtr.com.hk/data/mtr_lines_and_stations.csv"
        response = requests.get(stations_url, timeout=10)
        
        if response.status_code == 200:
            reader = csv.DictReader(io.StringIO(response.text))
            stations = list(reader)
            logger.info(f"✅ Successfully fetched {len(stations)} MTR stations")
            
            if stations:
                sample = stations[0]
                logger.info(f"Sample station: {sample}")
                
        else:
            logger.error(f"❌ MTR stations API returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error fetching MTR stations: {str(e)}")
    
    # Test facilities
    try:
        facilities_url = "https://opendata.mtr.com.hk/data/barrier_free_facilities.csv"
        response = requests.get(facilities_url, timeout=10)
        
        if response.status_code == 200:
            reader = csv.DictReader(io.StringIO(response.text))
            facilities = list(reader)
            logger.info(f"✅ Successfully fetched {len(facilities)} MTR accessibility facilities")
            
            if facilities:
                sample = facilities[0]
                logger.info(f"Sample facility: {sample}")
                
        else:
            logger.error(f"❌ MTR facilities API returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error fetching MTR facilities: {str(e)}")

def test_fehd_restaurant_xml():
    """Test FEHD restaurant XML"""
    logger.info("Testing FEHD restaurant XML...")
    
    try:
        url = "https://res.data.gov.hk/api/get-download-file?name=https%3A%2F%2Fwww.fehd.gov.hk%2Fenglish%2Flicensing%2Flicense%2Ftext%2FLP_Restaurants_EN.XML"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            logger.info(f"✅ Successfully fetched restaurant XML")
            logger.info(f"Root tag: {root.tag}")
            
            # Try to find restaurant elements
            restaurants = root.findall('.//restaurant') or root.findall('.//licence') or root.findall('.//*')
            logger.info(f"Found {len(restaurants)} XML elements")
            
            if restaurants:
                sample = restaurants[0]
                logger.info(f"Sample element tag: {sample.tag}")
                logger.info(f"Sample element attributes: {sample.attrib}")
                
        else:
            logger.error(f"❌ Restaurant XML API returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error fetching restaurant XML: {str(e)}")

def test_accessibility_xml():
    """Test accessibility XML feeds"""
    logger.info("Testing accessibility XML feeds...")
    
    # Test attractions
    try:
        attractions_url = "https://res.data.gov.hk/api/get-download-file?name=https%3A%2F%2Faccessguide.hk%2F%3Ffeed%3Datom%26post_type%3Dlocation%26type%3Dattractions"
        response = requests.get(attractions_url, timeout=15)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            logger.info(f"✅ Successfully fetched accessibility attractions XML")
            
            # Look for Atom entries
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            logger.info(f"Found {len(entries)} accessibility attraction entries")
            
        else:
            logger.error(f"❌ Accessibility attractions XML returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error fetching accessibility attractions XML: {str(e)}")
    
    # Test dining
    try:
        dining_url = "https://res.data.gov.hk/api/get-download-file?name=https%3A%2F%2Faccessguide.hk%2F%3Ffeed%3Datom%26post_type%3Dlocation%26type%3Dshopping-dining"
        response = requests.get(dining_url, timeout=15)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            logger.info(f"✅ Successfully fetched accessibility dining XML")
            
            # Look for Atom entries
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')
            logger.info(f"Found {len(entries)} accessibility dining entries")
            
        else:
            logger.error(f"❌ Accessibility dining XML returned status {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ Error fetching accessibility dining XML: {str(e)}")

def main():
    """Run all API tests"""
    logger.info("=== TESTING NEW HONG KONG GOVERNMENT APIs ===")
    
    test_hk_tourism_attractions()
    test_hk_weather_apis()
    test_mtr_apis()
    test_fehd_restaurant_xml()
    test_accessibility_xml()
    
    logger.info("=== API TESTING COMPLETE ===")

if __name__ == "__main__":
    main()