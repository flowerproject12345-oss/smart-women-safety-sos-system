"""
📋 Constants for ShieldHer
"""

# SOS Status
SOS_STATUS_ACTIVE = 'active'
SOS_STATUS_RESOLVED = 'resolved'
SOS_STATUS_CANCELLED = 'cancelled'

# Contact Relationship Types
RELATIONSHIP_TYPES = [
    'Mother',
    'Father',
    'Sister',
    'Brother',
    'Friend',
    'Spouse',
    'Relative',
    'Neighbor',
    'Other'
]

# Action Types
ACTION_SOS_TRIGGERED = 'sos_triggered'
ACTION_SOS_RESOLVED = 'sos_resolved'
ACTION_CONTACT_ADDED = 'contact_added'
ACTION_CONTACT_DELETED = 'contact_deleted'
ACTION_SAFE_ZONE_ADDED = 'safe_zone_added'
ACTION_SAFE_ZONE_DELETED = 'safe_zone_deleted'
ACTION_TRACKING_STARTED = 'tracking_started'
ACTION_TRACKING_STOPPED = 'tracking_stopped'
ACTION_FAKE_CALL_MADE = 'fake_call_made'

# Safe Zone Defaults
DEFAULT_SAFE_ZONE_RADIUS = 100  # meters
MAX_SAFE_ZONE_RADIUS = 1000  # meters

# Location Update Intervals
LOCATION_UPDATE_INTERVAL_NORMAL = 30000  # 30 seconds
LOCATION_UPDATE_INTERVAL_EMERGENCY = 5000  # 5 seconds

# SOS Settings
SOS_HOLD_DURATION = 3000  # 3 seconds
SOS_ALERT_DURATION = 30000  # 30 seconds

# Map Settings
DEFAULT_MAP_ZOOM = 15
DEFAULT_MAP_CENTER = {'lat': 13.0827, 'lng': 80.2707}  # Chennai

# Demo Mode
DEMO_MODE = True

# Emergency Numbers
EMERGENCY_NUMBERS = {
    'police': '100',
    'ambulance': '102',
    'fire': '101',
    'women_helpline': '1091'
}