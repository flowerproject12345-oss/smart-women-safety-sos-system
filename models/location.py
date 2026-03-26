"""
📍 Location History Model
"""

from database.database import get_db
from datetime import datetime

class LocationHistory:
    """Location history model"""
    
    @staticmethod
    def create(user_id, tracking_session_id, latitude, longitude, address, accuracy=None):
        """Record location point"""
        conn = get_db()
        conn.execute("""
            INSERT INTO location_history (user_id, tracking_session_id, latitude, longitude, address, accuracy)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, tracking_session_id, latitude, longitude, address, accuracy))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_locations(user_id, tracking_session_id=None, limit=100):
        """Get location history"""
        conn = get_db()
        if tracking_session_id:
            locations = conn.execute("""
                SELECT * FROM location_history 
                WHERE user_id = ? AND tracking_session_id = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, tracking_session_id, limit)).fetchall()
        else:
            locations = conn.execute("""
                SELECT * FROM location_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit)).fetchall()
        conn.close()
        return [dict(location) for location in locations]
    
    @staticmethod
    def get_last_location(user_id):
        """Get most recent location"""
        conn = get_db()
        location = conn.execute("""
            SELECT * FROM location_history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (user_id,)).fetchone()
        conn.close()
        return dict(location) if location else None