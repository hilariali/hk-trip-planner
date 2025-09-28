"""
Weather Service for Hong Kong Trip Planner
Integrates with Hong Kong weather APIs for trip planning
"""

import requests
import streamlit as st
from datetime import datetime, timedelta
from typing import List, Optional
from models import WeatherData

class WeatherService:
    """Service for fetching Hong Kong weather data"""
    
    def __init__(self):
        """Initialize weather service with API configuration"""
        self.base_url = st.secrets.get("weather", {}).get("base_url", "")
        self.api_key = st.secrets.get("weather", {}).get("api_key", "")
    
    def get_current_weather(self) -> WeatherData:
        """Get current weather conditions in Hong Kong"""
        try:
            # Try to fetch from Hong Kong Observatory API
            url = f"{self.base_url}weather.php?dataType=rhrread&lang=en"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_weather_data(data)
            else:
                # Fallback to mock data
                return self._get_mock_weather()
                
        except Exception as e:
            st.warning(f"Could not fetch live weather data: {str(e)}. Using default conditions.")
            return self._get_mock_weather()
    
    def get_forecast(self, days: int = 3) -> List[WeatherData]:
        """Get weather forecast for specified number of days"""
        try:
            # Try to fetch forecast data
            url = f"{self.base_url}weather.php?dataType=fnd&lang=en"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return self._parse_forecast_data(data, days)
            else:
                # Fallback to mock forecast
                return self._get_mock_forecast(days)
                
        except Exception as e:
            st.warning(f"Could not fetch weather forecast: {str(e)}. Using default forecast.")
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
    
    def _parse_weather_data(self, data: dict) -> WeatherData:
        """Parse Hong Kong Observatory weather data"""
        try:
            # Extract temperature (try different possible fields)
            temperature = 25.0  # default
            if 'temperature' in data:
                temperature = float(data['temperature'][0]['value'])
            elif 'temp' in data:
                temperature = float(data['temp'])
            
            # Extract humidity
            humidity = 70.0  # default
            if 'humidity' in data:
                humidity = float(data['humidity'][0]['value'])
            
            # Extract rainfall probability (may not be in current weather)
            rainfall_prob = 30.0  # default
            
            # Weather description
            weather_desc = "Partly cloudy"
            if 'weatherIcon' in data:
                weather_desc = data.get('weatherDesc', weather_desc)
            
            return WeatherData(
                temperature=temperature,
                humidity=humidity,
                rainfall_probability=rainfall_prob,
                weather_description=weather_desc,
                is_suitable_for_outdoor=self._is_outdoor_suitable(temperature, humidity, rainfall_prob)
            )
            
        except Exception as e:
            st.warning(f"Error parsing weather data: {str(e)}")
            return self._get_mock_weather()
    
    def _parse_forecast_data(self, data: dict, days: int) -> List[WeatherData]:
        """Parse forecast data from Hong Kong Observatory"""
        forecasts = []
        
        try:
            # Hong Kong Observatory forecast format
            if 'weatherForecast' in data:
                forecast_data = data['weatherForecast'][:days]
                
                for day_data in forecast_data:
                    temp_high = day_data.get('forecastMaxtemp', {}).get('value', 28)
                    temp_low = day_data.get('forecastMintemp', {}).get('value', 22)
                    avg_temp = (float(temp_high) + float(temp_low)) / 2
                    
                    humidity = day_data.get('forecastMaxrh', {}).get('value', 75)
                    weather_desc = day_data.get('forecastWeather', 'Partly cloudy')
                    
                    # Estimate rainfall probability from weather description
                    rainfall_prob = self._estimate_rainfall_from_description(weather_desc)
                    
                    forecasts.append(WeatherData(
                        temperature=avg_temp,
                        humidity=float(humidity),
                        rainfall_probability=rainfall_prob,
                        weather_description=weather_desc,
                        is_suitable_for_outdoor=self._is_outdoor_suitable(avg_temp, float(humidity), rainfall_prob)
                    ))
            
            # Fill remaining days with mock data if needed
            while len(forecasts) < days:
                forecasts.append(self._get_mock_weather())
                
        except Exception as e:
            st.warning(f"Error parsing forecast data: {str(e)}")
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