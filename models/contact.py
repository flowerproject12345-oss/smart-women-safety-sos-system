"""
👥 Emergency Contact Model
"""

from database.database import get_db
import json

class EmergencyContact:
    """Emergency contact model"""
    
    @staticmethod
    def create(user_id, name, phone, email=None, relationship=None, is_primary=False):
        """Add new emergency contact"""
        conn = get_db()
        cursor = conn.execute("""
            INSERT INTO emergency_contacts (user_id, name, phone, email, relationship, is_primary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, name, phone, email, relationship, 1 if is_primary else 0))
        
        # If this is primary, unset others
        if is_primary:
            conn.execute(
                "UPDATE emergency_contacts SET is_primary = 0 WHERE user_id = ? AND id != ?",
                (user_id, cursor.lastrowid)
            )
        
        conn.commit()
        contact_id = cursor.lastrowid
        conn.close()
        return contact_id
    
    @staticmethod
    def get_all(user_id):
        """Get all contacts for a user"""
        conn = get_db()
        contacts = conn.execute(
            "SELECT * FROM emergency_contacts WHERE user_id = ? ORDER BY is_primary DESC, created_at DESC",
            (user_id,)
        ).fetchall()
        conn.close()
        return [dict(contact) for contact in contacts]
    
    @staticmethod
    def delete(contact_id, user_id):
        """Delete a contact"""
        conn = get_db()
        conn.execute(
            "DELETE FROM emergency_contacts WHERE id = ? AND user_id = ?",
            (contact_id, user_id)
        )
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update(contact_id, user_id, **kwargs):
        """Update contact details"""
        conn = get_db()
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if value is not None:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            values.append(contact_id)
            values.append(user_id)
            conn.execute(
                f"UPDATE emergency_contacts SET {', '.join(updates)} WHERE id = ? AND user_id = ?",
                values
            )
            conn.commit()
        
        conn.close()
        return True