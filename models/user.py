"""
👤 User Model
"""

import sqlite3
from database.database import get_db

class User:
    """User model for authentication and user data"""
    
    @staticmethod
    def create(username, email, phone, password, full_name=None):
        """Create a new user"""
        conn = get_db()
        cursor = conn.execute("""
            INSERT INTO users (username, email, phone, password, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, phone, password, full_name))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return user_id
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def authenticate(username, password):
        """Authenticate user"""
        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE (username = ? OR email = ?) AND password = ?",
            (username, username, password)
        ).fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def update_last_login(user_id):
        """Update last login timestamp"""
        conn = get_db()
        conn.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user_id,)
        )
        conn.commit()
        conn.close()