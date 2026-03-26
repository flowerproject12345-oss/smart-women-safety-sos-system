"""
🏠 Safe Zone Model
"""

from database.database import get_db
from math import radians, sin, cos, sqrt, atan2

class SafeZone:
    """Safe zone model"""
    
    @staticmethod
    def create(user_id, name, latitude, longitude, address=None, radius=100):
        """Create new safe zone"""
        conn = get_db()
        cursor = conn.execute("""
            INSERT INTO safe_zones (user_id, name, latitude, longitude, address, radius)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, latitude, longitude, address, radius))
        conn.commit()
        zone_id = cursor.lastrowid
        conn.close()
        return zone_id
    
    @staticmethod
    def get_all(user_id):
        """Get all safe zones for a user"""
        conn = get_db()
        zones = conn.execute(
            "SELECT * FROM safe_zones WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
        conn.close()
        return [dict(zone) for zone in zones]
    
    @staticmethod
    def delete(zone_id, user_id):
        """Delete safe zone"""
        conn = get_db()
        conn.execute(
            "DELETE FROM safe_zones WHERE id = ? AND user_id = ?",
            (zone_id, user_id)
        )
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def check_proximity(user_id, latitude, longitude):
        """Check if user is near any safe zone"""
        zones = SafeZone.get_all(user_id)
        alerts = []
        
        for zone in zones:
            distance = SafeZone.calculate_distance(
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
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two points in meters using Haversine formula"""
        R = 6371000  # Earth's radius in meters
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c