"""
Climate Data Integration Module.
Fetches real environmental data from public APIs to show students real-world data.
"""

import requests
import json
from datetime import datetime
from config import OPEN_METEO_API_URL


class ClimateDataFetcher:
    """Fetches real-time climate and environmental data from public APIs."""
    
    @staticmethod
    def get_air_quality_data(latitude: float, longitude: float) -> dict:
        """
        Fetch air quality data for given coordinates using Open-Meteo API.
        
        Args:
            latitude: Geographic latitude
            longitude: Geographic longitude
            
        Returns:
            Dictionary with air quality information
        """
        try:
            # Open-Meteo Air Quality API
            url = 'https://air-quality-api.open-meteo.com/v1/air-quality'
            
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'us_aqi,pm10,pm2_5,nitrogen_dioxide,carbon_monoxide',
                'timezone': 'auto'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'current' in data:
                current = data['current']
                
                # Interpret AQI
                aqi = current.get('us_aqi', 0)
                aqi_category = ClimateDataFetcher._interpret_aqi(aqi)
                
                return {
                    'success': True,
                    'location': {
                        'latitude': latitude,
                        'longitude': longitude
                    },
                    'timestamp': current.get('time', datetime.now().isoformat()),
                    'air_quality': {
                        'us_aqi': aqi,
                        'category': aqi_category,
                        'pm10': current.get('pm10', 0),
                        'pm2_5': current.get('pm2_5', 0),
                        'nitrogen_dioxide': current.get('nitrogen_dioxide', 0),
                        'carbon_monoxide': current.get('carbon_monoxide', 0),
                    },
                    'health_recommendation': ClimateDataFetcher._get_health_recommendation(aqi_category)
                }
            
            return {'success': False, 'message': 'No data in response'}
        
        except requests.exceptions.RequestException as e:
            return {'success': False, 'message': f'API request failed: {str(e)}'}
        except Exception as e:
            return {'success': False, 'message': f'Error fetching air quality: {str(e)}'}
    
    @staticmethod
    def get_weather_data(latitude: float, longitude: float) -> dict:
        """
        Fetch weather data including temperature and precipitation.
        
        Args:
            latitude: Geographic latitude
            longitude: Geographic longitude
            
        Returns:
            Dictionary with weather information
        """
        try:
            url = 'https://api.open-meteo.com/v1/forecast'
            
            params = {
                'latitude': latitude,
                'longitude': longitude,
                'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
                'hourly': 'temperature_2m,precipitation',
                'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum',
                'timezone': 'auto',
                'temperature_unit': 'celsius'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'current' in data:
                current = data['current']
                
                return {
                    'success': True,
                    'location': {
                        'latitude': latitude,
                        'longitude': longitude
                    },
                    'current_weather': {
                        'temperature': current.get('temperature_2m', 0),
                        'humidity': current.get('relative_humidity_2m', 0),
                        'wind_speed': current.get('wind_speed_10m', 0),
                        'weather_code': current.get('weather_code', 0),
                        'time': current.get('time', datetime.now().isoformat())
                    },
                    'forecast': {
                        'daily': data.get('daily', {})
                    }
                }
            
            return {'success': False, 'message': 'No weather data'}
        
        except Exception as e:
            return {'success': False, 'message': f'Error fetching weather: {str(e)}'}
    
    @staticmethod
    def search_city_coordinates(city_name: str) -> dict:
        """
        Search for city coordinates using Open-Meteo Geocoding API.
        
        Args:
            city_name: Name of the city
            
        Returns:
            Dictionary with coordinates
        """
        try:
            url = 'https://geocoding-api.open-meteo.com/v1/search'
            
            params = {
                'name': city_name,
                'count': 1,
                'language': 'en',
                'format': 'json'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                
                return {
                    'success': True,
                    'city': result.get('name'),
                    'country': result.get('country'),
                    'latitude': result.get('latitude'),
                    'longitude': result.get('longitude'),
                    'timezone': result.get('timezone')
                }
            
            return {'success': False, 'message': f'City "{city_name}" not found'}
        
        except Exception as e:
            return {'success': False, 'message': f'Search failed: {str(e)}'}
    
    @staticmethod
    def _interpret_aqi(aqi_value: int) -> str:
        """Interpret AQI value into category."""
        if aqi_value <= 50:
            return 'Good'
        elif aqi_value <= 100:
            return 'Moderate'
        elif aqi_value <= 150:
            return 'Unhealthy for Sensitive Groups'
        elif aqi_value <= 200:
            return 'Unhealthy'
        elif aqi_value <= 300:
            return 'Very Unhealthy'
        else:
            return 'Hazardous'
    
    @staticmethod
    def _get_health_recommendation(aqi_category: str) -> str:
        """Get health recommendation based on AQI category."""
        recommendations = {
            'Good': 'Air quality is satisfactory. Enjoy outdoor activities!',
            'Moderate': 'Air quality is acceptable. Unusually sensitive people should consider outdoor activity limitations.',
            'Unhealthy for Sensitive Groups': 'Sensitive groups should limit outdoor activities.',
            'Unhealthy': 'Everyone should limit outdoor activities. Wear a mask if going outside.',
            'Very Unhealthy': 'Avoid outdoor activities. Wear N95 mask if you must go outside.',
            'Hazardous': 'Stay indoors and keep activity levels low. Use air purifier if possible.'
        }
        
        return recommendations.get(aqi_category, 'Check air quality updates.')
    
    @staticmethod
    def get_co2_emission_data(country: str = None) -> dict:
        """
        Fetch CO2 emission data (placeholder for educational data).
        In production, would integrate with real climate API like World Bank or NASA.
        
        Args:
            country: Optional country filter
            
        Returns:
            CO2 emission statistics
        """
        # This is a placeholder - would connect to real climate data API
        return {
            'success': True,
            'data': {
                'message': 'CO2 data integration requires dedicated climate API key',
                'note': 'Consider integrating with World Bank API, NASA GISS, or similar'
            }
        }


class EnvironmentalDataAnalyzer:
    """Analyzes environmental data for educational insights."""
    
    @staticmethod
    def compare_air_quality_historical(data_points: list) -> dict:
        """
        Analyze air quality trends.
        
        Args:
            data_points: List of air quality measurements over time
            
        Returns:
            Analysis and trends
        """
        if not data_points:
            return {'success': False, 'message': 'No data points'}
        
        aqi_values = [d['us_aqi'] for d in data_points if 'us_aqi' in d]
        
        if not aqi_values:
            return {'success': False, 'message': 'No AQI values found'}
        
        average_aqi = sum(aqi_values) / len(aqi_values)
        max_aqi = max(aqi_values)
        min_aqi = min(aqi_values)
        
        # Detect trend
        if len(aqi_values) > 1:
            recent_avg = sum(aqi_values[-3:]) / min(3, len(aqi_values))
            older_avg = sum(aqi_values[:-3]) / max(1, len(aqi_values) - 3)
            trend = 'improving' if recent_avg < older_avg else 'worsening' if recent_avg > older_avg else 'stable'
        else:
            trend = 'insufficient data'
        
        return {
            'success': True,
            'statistics': {
                'average_aqi': round(average_aqi, 2),
                'max_aqi': max_aqi,
                'min_aqi': min_aqi,
                'trend': trend,
                'data_points': len(aqi_values)
            }
        }
    
    @staticmethod
    def calculate_carbon_footprint_educational(activity: str, amount: float) -> dict:
        """
        Calculate estimated carbon footprint for educational purposes.
        
        Args:
            activity: Type of activity (car_drive, flight, electricity)
            amount: Amount (km, hours, kWh, etc.)
            
        Returns:
            CO2 equivalent in kg
        """
        # Conversion factors (simplified for education)
        factors = {
            'car_drive': 0.21,  # kg CO2 per km
            'bus_ride': 0.089,  # kg CO2 per km
            'flight_hour': 90,  # kg CO2 per hour
            'electricity_hour': 0.4,  # kg CO2 per kWh (varies by region)
            'meat_meal': 6.6,  # kg CO2 per meal
            'plant_meal': 0.51,  # kg CO2 per meal
        }
        
        if activity not in factors:
            return {'success': False, 'message': f'Unknown activity: {activity}'}
        
        co2_kg = amount * factors[activity]
        
        return {
            'success': True,
            'activity': activity,
            'amount': amount,
            'co2_equivalent_kg': round(co2_kg, 2),
            'co2_equivalent_tons': round(co2_kg / 1000, 4),
            'equivalent_trees_to_offset': round(co2_kg / 21, 1)  # Average tree absorbs 21kg CO2/year
        }
