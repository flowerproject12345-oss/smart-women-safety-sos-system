"""
⚙️ ShieldHer Configuration Settings
"""

import os

class Config:
    """Configuration class for ShieldHer"""
    
    # 🔐 Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # 📁 Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'shieldher.db')
    
    # 📱 Twilio SMS (Optional - get from https://www.twilio.com)
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER', '')
    
    # 📧 Email (Optional - for Gmail)
    EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', '')
    EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
    
    # 🗺️ Google Maps API (Optional)
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY', '')
    
    # 🧪 Demo Mode (True = no actual SMS/Email sent)
    DEMO_MODE = True
    
    # ⏱️ SOS Settings
    SOS_HOLD_DURATION = 3000  # milliseconds (3 seconds)
    LOCATION_UPDATE_INTERVAL = 5000  # 5 seconds
    
    # 🏠 Safe Zone Settings
    SAFE_ZONE_RADIUS = 100  # meters
    
    # 📍 Default Location (Chennai, India)
    DEFAULT_LATITUDE = 13.0827
    DEFAULT_LONGITUDE = 80.2707
    DEFAULT_ADDRESS = "Chennai, Tamil Nadu, India"