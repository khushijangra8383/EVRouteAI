# api_client.py
import requests
import streamlit as st

def get_coordinates(city_name, api_key):
    """Converts a city name into [longitude, latitude] coordinates."""
    url = f"https://api.openrouteservice.org/geocode/search?api_key={api_key}&text={city_name}&size=1"
    try:
        response = requests.get(url).json()
        coords = response['features'][0]['geometry']['coordinates']
        return coords
    except Exception:
        return None

def get_route_with_elevation(start_coords, end_coords, api_key):
    """Fetches driving coordinates along with 3D elevation profile profiles."""
    url = f"https://api.openrouteservice.org/v2/directions/driving-car/geojson?api_key={api_key}"
    body = {"coordinates": [start_coords, end_coords], "elevation": True}
    try:
        response = requests.post(url, json=body).json()
        if 'error' in response:
            st.error(f"API Error: {response['error'].get('message', 'Route not found')}")
            return None, None, None
            
        geometry = response['features'][0]['geometry']['coordinates']
        properties = response['features'][0]['properties']['segments'][0]
        distance_km = properties['distance'] / 1000.0
        duration_hrs = properties['duration'] / 3600.0
        return geometry, distance_km, duration_hrs
    except Exception:
        return None, None, None

def get_weather_data(lat, lon, api_key):
    """Fetches real-time localized environmental weather constraints."""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    try:
        res = requests.get(url).json()
        weather_main = res['weather'][0]['main'].lower()
        wind_speed = res['wind']['speed']
        temp = res['main']['temp']
        is_raining = True if "rain" in weather_main or "drizzle" in weather_main else False
        return wind_speed, temp, is_raining
    except Exception:
        return 0, 25, False