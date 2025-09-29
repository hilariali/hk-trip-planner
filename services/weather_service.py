"""
Weather Service for Hong Kong Trip Planner
Integrates with Hong Kong weather APIs for trip planning
"""

import requests
import streamlit as st
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from models import WeatherData

# Configure logging
logger = logging.getLogger(__name__)

class WeatherService:
    """Service for fetching Hong Kong weather data"""
    
    def __init__(self):
        """Initialize weather service with API configuration"""
        try:
            self.base_url = st.secrets.get("weather", {}).get("base_url", "")
            self.api_key = st.secrets.get("weather", {}).get("api_key", "")
        except:
            # Fallback when not running in Streamlit context
            self.base_url = ""
            self.api_key = ""
    
    def get_current_weather(self) -> WeatherData:
        """Get current weather conditions from Hong Kong Observatory"""
        try:
            # Use Hong Kong Observatory official API
            hko_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en"
            response = requests.get(hko_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_hko_weather_data(data)
            else:
                logger.warning(f"HKO API returned status {response.status_code}")
                return self._get_mock_weather()
                
        except Exception as e:
            logger.info(f"Using default weather conditions: {str(e)}")
            return self._get_mock_weather()
    
    def get_forecast(self, days: int = 3) -> List[WeatherData]:
        """Get weather forecast from Hong Kong Observatory"""
        try:
            # Use HKO official forecast API
            hko_forecast_url = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang=en"
            response = requests.get(hko_forecast_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_hko_forecast_data(data, days)
            else:
                logger.warning(f"HKO forecast API returned status {response.status_code}")
                return self._get_mock_forecast(days)
                
        except Exception as e:
            logger.info(f"Using default forecast: {str(e)}")
            return self._get_mock_forecast(days)
    
    def recommend_indoor_outdoor_ratio(self, weather: WeatherData) -> float:
        """Recommend ratio of indoor to outdoor activities based on weather"""
        if weather.rainfall_probability > 70:
            return 0.8  # 80% indoor activities
        elif weather.rainfall_probability > 40:
            return 0.6  # 60% indoor activities
        elif weather.temperature > 32 or weather.temperature < 15:
            return 0.5  # 50% indoor activities
        else:
            return 0.3  # 30% indoor activities (mostly outdoor)
    
    def is_suitable_for_seniors(self, weather: WeatherData) -> bool:
        """Check if weather conditions are suitable for seniors"""
        # Avoid extreme temperatures and high rainfall
        if weather.temperature < 12 or weather.temperature > 35:
            return False
        if weather.rainfall_probability > 60:
            return False
        if weather.humidity > 85:
            return False
        return True
    
    def _parse_hko_weather_data(self, data: dict) -> WeatherData:
        """Parse Hong Kong Observatory official API weather data"""
        try:
            # Extract temperature from HKO API format
            temperature = 25.0  # default
            if 'temperature' in data and data['temperature']:
                for temp_data in data['temperature']:
                    if temp_data.get('place') == 'Hong Kong Observatory':
                        temperature = float(temp_data['value'])
                        break
                else:
                    # Use first available temperature reading
                    temperature = float(data['temperature'][0]['value'])
            
            # Extract humidity
            humidity = 70.0  # default
            if 'humidity' in data and data['humidity']:
                for humid_data in data['humidity']:
                    if humid_data.get('place') == 'Hong Kong Observatory':
                        humidity = float(humid_data['value'])
                        break
                else:
                    humidity = float(data['humidity'][0]['value'])
            
            # Extract rainfall (if available)
            rainfall_prob = 30.0  # default
            if 'rainfall' in data and data['rainfall']:
                # Calculate rainfall probability based on recent rainfall
                recent_rainfall = sum(float(r.get('main', 0)) for r in data['rainfall'][:3])
                if recent_rainfall > 10:
                    rainfall_prob = 70.0
                elif recent_rainfall > 2:
                    rainfall_prob = 50.0
                else:
                    rainfall_prob = 20.0
            
            # Weather description
            weather_desc = "Partly cloudy"
            if 'icon' in data and data['icon']:
                icon_code = data['icon'][0]
                weather_desc = self._icon_to_description(icon_code)
            
            return WeatherData(
                temperature=temperature,
                humidity=humidity,
                rainfall_probability=rainfall_prob,
                weather_description=weather_desc,
                is_suitable_for_outdoor=self._is_outdoor_suitable(temperature, humidity, rainfall_prob)
            )
            
        except Exception as e:
            logger.warning(f"Error parsing HKO weather data: {str(e)}")
            return self._get_mock_weather()
    
    def _icon_to_description(self, icon_code: int) -> str:
        """Convert HKO weather icon code to description"""
        icon_descriptions = {
            50: "Sunny",
            51: "Sunny periods",
            52: "Sunny intervals",
            53: "Sunny periods with a few showers",
            54: "Sunny intervals with showers",
            60: "Cloudy",
            61: "Overcast",
            62: "Light rain",
            63: "Rain",
            64: "Heavy rain",
            65: "Thunderstorms",
            70: "Fine",
            71: "Partly cloudy",
            72: "Cloudy with sunny periods",
            73: "Cloudy with occasional showers",
            74: "Cloudy with showers",
            75: "Cloudy with heavy showers",
            76: "Cloudy with thunderstorms",
            77: "Hot",
            80: "Windy",
            81: "Dry",
            82: "Humid",
            83: "Foggy",
            84: "Misty",
            85: "Hazy"
        }
        return icon_descriptions.get(icon_code, "Partly cloudy")
    
    def _parse_hko_forecast_data(self, data: dict, days: int) -> List[WeatherData]:
        """Parse forecast data from Hong Kong Observatory official API"""
        forecasts = []
        
        try:
            # HKO forecast format
            if 'weatherForecast' in data:
                forecast_data = data['weatherForecast'][:days]
                
                for day_data in forecast_data:
                    # Temperature
                    temp_high = day_data.get('forecastMaxtemp', {}).get('value', 28)
                    temp_low = day_data.get('forecastMintemp', {}).get('value', 22)
                    avg_temp = (float(temp_high) + float(temp_low)) / 2
                    
                    # Humidity
                    humidity_min = day_data.get('forecastMinrh', {}).get('value', 60)
                    humidity_max = day_data.get('forecastMaxrh', {}).get('value', 85)
                    avg_humidity = (float(humidity_min) + float(humidity_max)) / 2
                    
                    # Weather description
                    weather_desc = day_data.get('forecastWeather', 'Partly cloudy')
                    
                    # Rainfall probability from weather description and PSR
                    rainfall_prob = self._estimate_rainfall_from_description(weather_desc)
                    if 'PSR' in day_data:
                        rainfall_prob = max(rainfall_prob, float(day_data['PSR']))
                    
                    forecasts.append(WeatherData(
                        temperature=avg_temp,
                        humidity=avg_humidity,
                        rainfall_probability=rainfall_prob,
                        weather_description=weather_desc,
                        is_suitable_for_outdoor=self._is_outdoor_suitable(avg_temp, avg_humidity, rainfall_prob)
                    ))
            
            # Fill remaining days with mock data if needed
            while len(forecasts) < days:
                forecasts.append(self._get_mock_weather())
                
        except Exception as e:
            logger.warning(f"Error parsing HKO forecast data: {str(e)}")
            return self._get_mock_forecast(days)
        
        return forecasts
    
    def _estimate_rainfall_from_description(self, description: str) -> float:
        """Estimate rainfall probability from weather description"""
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['heavy rain', 'thunderstorm', 'storm']):
            return 80.0
        elif any(word in description_lower for word in ['rain', 'shower', 'drizzle']):
            return 60.0
        elif any(word in description_lower for word in ['cloudy', 'overcast']):
            return 30.0
        else:
            return 15.0
    
    def _is_outdoor_suitable(self, temperature: float, humidity: float, rainfall_prob: float) -> bool:
        """Determine if conditions are suitable for outdoor activities"""
        if rainfall_prob > 50:
            return False
        if temperature < 15 or temperature > 33:
            return False
        if humidity > 90:
            return False
        return True
    
    def _get_mock_weather(self) -> WeatherData:
        """Get mock weather data for testing/fallback"""
        return WeatherData(
            temperature=25.0,
            humidity=70.0,
            rainfall_probability=20.0,
            weather_description="Partly cloudy with mild temperatures",
            is_suitable_for_outdoor=True
        )
    
    def _get_mock_forecast(self, days: int) -> List[WeatherData]:
        """Get mock forecast data for testing/fallback"""
        forecasts = []
        base_temp = 25.0
        
        for i in range(days):
            # Vary temperature slightly each day
            temp = base_temp + (i * 2) - 1
            rainfall = 20.0 + (i * 10)  # Gradually increasing chance of rain
            
            forecasts.append(WeatherData(
                temperature=temp,
                humidity=70.0 + (i * 5),
                rainfall_probability=min(rainfall, 70.0),
                weather_description=f"Day {i+1}: Partly cloudy",
                is_suitable_for_outdoor=rainfall < 50
            ))
        
        return forecasts