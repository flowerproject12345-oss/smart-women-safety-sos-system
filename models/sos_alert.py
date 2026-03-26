"""
🚨 SOS Alert Model
"""

from database.database import get_db
from datetime import datetime

class SOSAlert:
    """SOS alert model"""
    
    @staticmethod
    def create(user_id, latitude, longitude, address):
        """Create new SOS alert"""
        conn = get_db()
        cursor = conn.execute("""
            INSERT INTO sos_alerts (user_id, latitude, longitude, address, status)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, latitude, longitude, address, 'active'))
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        return alert_id
    
    @staticmethod
    def get_all(user_id, limit=50):
        """Get all alerts for a user"""
        conn = get_db()
        alerts = conn.execute("""
            SELECT * FROM sos_alerts 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (user_id, limit)).fetchall()
        conn.close()
        return [dict(alert) for alert in alerts]
    
    @staticmethod
    def get_active(user_id):
        """Get active SOS alerts"""
        conn = get_db()
        alerts = conn.execute("""
            SELECT * FROM sos_alerts 
            WHERE user_id = ? AND status = 'active'
            ORDER BY timestamp DESC
        """, (user_id,)).fetchall()
        conn.close()
        return [dict(alert) for alert in alerts]
    
    @staticmethod
    def resolve(alert_id, user_id):
        """Resolve SOS alert"""
        conn = get_db()
        conn.execute("""
            UPDATE sos_alerts 
            SET status = 'resolved', resolved_at = ?
            WHERE id = ? AND user_id = ?
        """, (datetime.now(), alert_id, user_id))
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_stats(user_id):
        """Get SOS statistics"""
        conn = get_db()
        
        total = conn.execute(
            "SELECT COUNT(*) as count FROM sos_alerts WHERE user_id = ?",
            (user_id,)
        ).fetchone()['count']
        
        active = conn.execute(
            "SELECT COUNT(*) as count FROM sos_alerts WHERE user_id = ? AND status = 'active'",
            (user_id,)
        ).fetchone()['count']
        
        resolved = conn.execute(
            "SELECT COUNT(*) as count FROM sos_alerts WHERE user_id = ? AND status = 'resolved'",
            (user_id,)
        ).fetchone()['count']
        
        conn.close()
        
        return {
            'total': total,
            'active': active,
            'resolved': resolved
        }