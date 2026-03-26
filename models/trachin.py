"""
📍 Tracking Session Model
"""

from database.database import get_db
from datetime import datetime

class TrackingSession:
    """Tracking session model"""
    
    @staticmethod
    def create(user_id, session_id):
        """Create new tracking session"""
        conn = get_db()
        conn.execute("""
            INSERT INTO tracking_sessions (user_id, session_id, is_active)
            VALUES (?, ?, 1)
        """, (user_id, session_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def stop(user_id):
        """Stop active tracking session"""
        conn = get_db()
        conn.execute("""
            UPDATE tracking_sessions 
            SET is_active = 0, end_time = ?
            WHERE user_id = ? AND is_active = 1
        """, (datetime.now(), user_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_active(user_id):
        """Get active tracking session"""
        conn = get_db()
        session = conn.execute("""
            SELECT * FROM tracking_sessions 
            WHERE user_id = ? AND is_active = 1
        """, (user_id,)).fetchone()
        conn.close()
        return dict(session) if session else None
    
    @staticmethod
    def get_history(user_id, limit=50):
        """Get tracking history"""
        conn = get_db()
        sessions = conn.execute("""
            SELECT * FROM tracking_sessions 
            WHERE user_id = ? 
            ORDER BY start_time DESC 
            LIMIT ?
        """, (user_id, limit)).fetchall()
        conn.close()
        return [dict(session) for session in sessions]