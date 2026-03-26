"""
🗄️ Database operations for ShieldHer
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'shieldher.db')

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database with all tables"""
    conn = get_db()
    cursor = conn.cursor()
    
    # 👤 Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # 👥 Emergency Contacts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT,
            relationship TEXT,
            is_primary BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 🚨 SOS Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            latitude REAL,
            longitude REAL,
            address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            resolved_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 🏠 Safe Zones Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS safe_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            address TEXT,
            radius INTEGER DEFAULT 100,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 📍 Tracking Sessions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracking_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_id TEXT UNIQUE NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    # 📊 Location History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS location_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            tracking_session_id INTEGER,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (tracking_session_id) REFERENCES tracking_sessions (id)
        )
    ''')
    
    # 📝 Action History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS action_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            action_type TEXT NOT NULL,
            action_details TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

# Insert demo user for testing
def insert_demo_user():
    """Insert a demo user for testing"""
    conn = get_db()
    
    # Check if demo user exists
    user = conn.execute("SELECT * FROM users WHERE username = 'demo_user'").fetchone()
    
    if not user:
        conn.execute("""
            INSERT INTO users (username, email, phone, password, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, ('demo_user', 'demo@shieldher.com', '+1234567890', 'demo123', 'Demo User'))
        
        user_id = cursor.lastrowid
        
        # Add demo contacts
        conn.execute("""
            INSERT INTO emergency_contacts (user_id, name, phone, email, relationship, is_primary)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, 'Mom', '+1234567891', 'mom@example.com', 'Mother', 1))
        
        conn.execute("""
            INSERT INTO emergency_contacts (user_id, name, phone, email, relationship)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, 'Dad', '+1234567892', 'dad@example.com', 'Father'))
        
        conn.execute("""
            INSERT INTO emergency_contacts (user_id, name, phone, email, relationship)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, 'Sister', '+1234567893', 'sister@example.com', 'Sister'))
        
        conn.commit()
        print("✅ Demo user created!")
    
    conn.close()

if __name__ == '__main__':
    init_database()
    insert_demo_user()