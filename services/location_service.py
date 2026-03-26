"""
📍 Location Services - Geocoding and location utilities
"""

import requests
from math import radians, sin, cos, sqrt, atan2
from config import Config
from models.safe_zone import SafeZone

def get_address_from_coordinates(latitude, longitude):
    """Get address from coordinates using reverse geocoding"""
    try:
        if Config.GOOGLE_MAPS_API_KEY:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={latitude},{longitude}&key={Config.GOOGLE_MAPS_API_KEY}"
            response = requests.get(url, timeout=5)
            data = response.json()
            if data['results']:
                return data['results'][0]['formatted_address']
        
        # Fallback
        return f"{latitude:.6f}, {longitude:.6f}"
        
    except Exception as e:
        print(f"❌ Geocoding Error: {e}")
        return f"{latitude:.6f}, {longitude:.6f}"

def get_coordinates_from_address(address):
    """Get coordinates from address using geocoding"""
    try:
        if Config.GOOGLE_MAPS_API_KEY:
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={Config.GOOGLE_MAPS_API_KEY}"
            response = requests.get(url, timeout=5)
            data = response.json()
            if data['results']:
                location = data['results'][0]['geometry']['location']
                return {
                    'latitude': location['lat'],
                    'longitude': location['lng'],
                    'formatted_address': data['results'][0]['formatted_address']
                }
    except Exception as e:
        print(f"❌ Geocoding Error: {e}")
    
    return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points in meters using Haversine formula"""
    R = 6371000  # Earth's radius in meters
    
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    return R * c

def check_safe_zone_proximity(user_id, latitude, longitude):
    """Check if user is near any safe zone"""
    zones = SafeZone.get_all(user_id)
    alerts = []
    
    for zone in zones:
        distance = calculate_distance(
            latitude, longitude,
            zone['latitude'], zone['longitude']
        )
        
        if distance <= zone['radius']:
            alerts.append({
                'zone_id': zone['id'],
                'zone_name': zone['name'],
                'distance': round(distance, 2),
                'is_inside': True
            })
    
    return alerts