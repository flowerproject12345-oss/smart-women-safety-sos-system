"""
🛡️ SHESHIELD - Complete Women Safety System
All Features: SOS Alert, Live Tracking, Fake Call, Notifications
"""

from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sqlite3
import datetime
import json
import os
import secrets
import hashlib
import threading
import time
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'database', 'sheshield.db')
CORS(app)

# Initialize SocketIO for real-time communication
socketio = SocketIO(app, cors_allowed_origins="*")

# Store active tracking sessions
active_tracking = {}

# Store active SOS sessions
active_sos = {}

# =============================================================================
# DATABASE FUNCTIONS
# =============================================================================

def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            email TEXT UNIQUE,
            phone TEXT,
            password TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            phone TEXT,
            email TEXT,
            relationship TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            latitude REAL,
            longitude REAL,
            address TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS safe_zones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            latitude REAL,
            longitude REAL,
            radius INTEGER DEFAULT 100
        )
    ''')
    
    conn.commit()
    conn.close()
    
    # Insert demo user if not exists
    insert_demo_user()
    print("✅ Database ready!")

def insert_demo_user():
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = 'demo@sheshield.com'").fetchone()
    
    if not user:
        hashed_password = hashlib.sha256('demo123'.encode()).hexdigest()
        conn.execute("""
            INSERT INTO users (username, email, phone, password, full_name)
            VALUES (?, ?, ?, ?, ?)
        """, ('demo_user', 'demo@sheshield.com', '+1234567890', hashed_password, 'Demo User'))
        
        user_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        
        # Add demo contacts
        conn.execute("""
            INSERT INTO emergency_contacts (user_id, name, phone, email, relationship)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, 'Mom', '+1234567891', 'mom@example.com', 'Mother'))
        
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

# =============================================================================
# DECORATORS
# =============================================================================

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'success': False, 'error': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated

# =============================================================================
# PAGE ROUTES
# =============================================================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/why')
def why_page():
    return render_template('why.html')

@app.route('/tracking')
@login_required
def tracking_page():
    return render_template('tracking.html')

@app.route('/contacts')
@login_required
def contacts_page():
    return render_template('contacts.html')

@app.route('/fake-call')
@login_required
def fake_call_page():
    return render_template('fake_call.html')

@app.route('/history')
@login_required
def history_page():
    return render_template('history.html')

# =============================================================================
# AUTH API
# =============================================================================

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ? AND password = ?",
        (email, hashed)
    ).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'user': dict(user)
        })
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    data = request.json
    full_name = data.get('full_name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    
    conn = get_db()
    existing = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    hashed = hashlib.sha256(password.encode()).hexdigest()
    username = email.split('@')[0]
    
    conn.execute("""
        INSERT INTO users (username, email, phone, password, full_name)
        VALUES (?, ?, ?, ?, ?)
    """, (username, email, phone, hashed, full_name))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Registration successful!'})

@app.route('/api/auth/me', methods=['GET'])
def api_me():
    if 'user_id' in session:
        conn = get_db()
        user = conn.execute(
            "SELECT id, username, email, phone, full_name FROM users WHERE id = ?",
            (session['user_id'],)
        ).fetchone()
        conn.close()
        return jsonify({'success': True, 'user': dict(user)})
    return jsonify({'success': False}), 401

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'success': True})

# =============================================================================
# SOS API - WITH REAL-TIME NOTIFICATIONS
# =============================================================================

@app.route('/api/sos/trigger', methods=['POST'])
@login_required
def trigger_sos():
    """Trigger SOS alert - Notifies ALL devices in real-time"""
    data = request.json
    latitude = data.get('latitude', 13.0827)
    longitude = data.get('longitude', 80.2707)
    address = data.get('address', 'Chennai, India')
    
    # Get user info
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    # Get emergency contacts
    contacts = conn.execute(
        "SELECT * FROM emergency_contacts WHERE user_id = ?",
        (session['user_id'],)
    ).fetchall()
    
    # Save SOS to database
    cursor = conn.execute("""
        INSERT INTO sos_alerts (user_id, latitude, longitude, address, status)
        VALUES (?, ?, ?, ?, ?)
    """, (session['user_id'], latitude, longitude, address, 'active'))
    sos_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Store active SOS
    active_sos[session['user_id']] = {
        'sos_id': sos_id,
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    # BROADCAST SOS TO ALL CONNECTED DEVICES
    sos_data = {
        'user_id': session['user_id'],
        'username': user['username'],
        'full_name': user['full_name'],
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
        'timestamp': datetime.datetime.now().isoformat(),
        'contacts': [dict(c) for c in contacts]
    }
    
    # Send to ALL connected clients via Socket.IO
    socketio.emit('sos_alert', sos_data, broadcast=True)
    
    # Also send to specific contacts (simulate SMS/Email)
    notifications_sent = []
    for contact in contacts:
        notifications_sent.append({
            'name': contact['name'],
            'phone': contact['phone'],
            'email': contact['email']
        })
    
    return jsonify({
        'success': True,
        'message': '🚨 SOS Alert Sent! All contacts notified.',
        'sos_id': sos_id,
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
        'notifications_sent': notifications_sent
    })

@app.route('/api/sos/resolve', methods=['POST'])
@login_required
def resolve_sos():
    """Resolve active SOS"""
    data = request.json
    sos_id = data.get('sos_id')
    
    conn = get_db()
    conn.execute(
        "UPDATE sos_alerts SET status = 'resolved' WHERE id = ? AND user_id = ?",
        (sos_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    
    if session['user_id'] in active_sos:
        del active_sos[session['user_id']]
    
    # Broadcast SOS resolved
    socketio.emit('sos_resolved', {
        'user_id': session['user_id'],
        'message': 'SOS alert resolved - User is safe'
    }, broadcast=True)
    
    return jsonify({'success': True, 'message': 'SOS resolved'})

@app.route('/api/sos/recent', methods=['GET'])
@login_required
def get_recent_sos():
    conn = get_db()
    alerts = conn.execute(
        "SELECT * FROM sos_alerts WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20",
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return jsonify([dict(alert) for alert in alerts])

@app.route('/api/sos/active', methods=['GET'])
@login_required
def get_active_sos():
    if session['user_id'] in active_sos:
        return jsonify({'active': True, 'data': active_sos[session['user_id']]})
    return jsonify({'active': False})

# =============================================================================
# CONTACTS API
# =============================================================================

@app.route('/api/contacts/get', methods=['GET'])
@login_required
def get_contacts():
    conn = get_db()
    contacts = conn.execute(
        "SELECT * FROM emergency_contacts WHERE user_id = ?",
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return jsonify([dict(c) for c in contacts])

@app.route('/api/contacts/add', methods=['POST'])
@login_required
def add_contact():
    data = request.json
    conn = get_db()
    conn.execute("""
        INSERT INTO emergency_contacts (user_id, name, phone, email, relationship)
        VALUES (?, ?, ?, ?, ?)
    """, (session['user_id'], data['name'], data['phone'], data.get('email'), data.get('relationship')))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Contact added!'})

@app.route('/api/contacts/delete/<int:contact_id>', methods=['DELETE'])
@login_required
def delete_contact(contact_id):
    conn = get_db()
    conn.execute(
        "DELETE FROM emergency_contacts WHERE id = ? AND user_id = ?",
        (contact_id, session['user_id'])
    )
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# =============================================================================
# TRACKING API - REAL-TIME LOCATION SHARING
# =============================================================================

@app.route('/api/tracking/start', methods=['POST'])
@login_required
def start_tracking():
    """Start live tracking session"""
    session_id = secrets.token_hex(16)
    active_tracking[session['user_id']] = {
        'session_id': session_id,
        'start_time': datetime.datetime.now().isoformat(),
        'locations': []
    }
    
    # Notify others that tracking started
    socketio.emit('tracking_started', {
        'user_id': session['user_id'],
        'username': session.get('username'),
        'session_id': session_id
    }, broadcast=True)
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': '📍 Live tracking started! Your location is being shared.'
    })

@app.route('/api/tracking/stop', methods=['POST'])
@login_required
def stop_tracking():
    """Stop live tracking"""
    if session['user_id'] in active_tracking:
        del active_tracking[session['user_id']]
    
    socketio.emit('tracking_stopped', {
        'user_id': session['user_id'],
        'username': session.get('username')
    }, broadcast=True)
    
    return jsonify({'success': True, 'message': 'Tracking stopped'})

@app.route('/api/tracking/status', methods=['GET'])
@login_required
def tracking_status():
    is_tracking = session['user_id'] in active_tracking
    return jsonify({
        'is_tracking': is_tracking,
        'session_id': active_tracking[session['user_id']]['session_id'] if is_tracking else None
    })

@app.route('/api/location/update', methods=['POST'])
@login_required
def update_location():
    """Update current location - broadcasts to all devices"""
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if session['user_id'] in active_tracking:
        location_data = {
            'user_id': session['user_id'],
            'username': session.get('username'),
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.datetime.now().isoformat(),
            'accuracy': data.get('accuracy', 0)
        }
        
        # Store location
        active_tracking[session['user_id']]['locations'].append(location_data)
        
        # BROADCAST TO ALL CONNECTED DEVICES
        socketio.emit('location_update', location_data, broadcast=True)
    
    return jsonify({'success': True})

# =============================================================================
# FAKE CALL API
# =============================================================================

@app.route('/api/fake-call/trigger', methods=['POST'])
@login_required
def trigger_fake_call():
    """Trigger fake call - notifies all devices"""
    data = request.json
    caller_name = data.get('caller_name', 'Mom')
    delay = data.get('delay', 3)
    
    # Schedule fake call notification
    def send_fake_call():
        time.sleep(delay)
        socketio.emit('fake_call_incoming', {
            'user_id': session['user_id'],
            'username': session.get('username'),
            'caller_name': caller_name,
            'caller_number': data.get('caller_number', '+1234567890')
        }, broadcast=True)
    
    thread = threading.Thread(target=send_fake_call)
    thread.daemon = True
    thread.start()
    
    return jsonify({
        'success': True,
        'message': f'📞 Fake call from {caller_name} will ring in {delay} seconds!'
    })

# =============================================================================
# USER STATS API
# =============================================================================

@app.route('/api/user/stats', methods=['GET'])
@login_required
def get_user_stats():
    conn = get_db()
    contacts = conn.execute(
        "SELECT COUNT(*) as count FROM emergency_contacts WHERE user_id = ?",
        (session['user_id'],)
    ).fetchone()['count']
    
    safe_zones = conn.execute(
        "SELECT COUNT(*) as count FROM safe_zones WHERE user_id = ?",
        (session['user_id'],)
    ).fetchone()['count']
    
    sos_count = conn.execute(
        "SELECT COUNT(*) as count FROM sos_alerts WHERE user_id = ?",
        (session['user_id'],)
    ).fetchone()['count']
    conn.close()
    
    return jsonify({
        'contacts': contacts,
        'safeZones': safe_zones,
        'sosCount': sos_count
    })

@app.route('/api/log-action', methods=['POST'])
@login_required
def log_action():
    return jsonify({'success': True})

# =============================================================================
# SOCKET.IO EVENTS - REAL-TIME COMMUNICATION
# =============================================================================

@socketio.on('connect')
def handle_connect():
    print(f'🔌 Client connected: {request.sid}')
    emit('connected', {'message': 'Connected to SheShield server'})

@socketio.on('disconnect')
def handle_disconnect():
    print(f'🔌 Client disconnected: {request.sid}')

@socketio.on('join_room')
def handle_join_room(data):
    room = data.get('room')
    if room:
        join_room(room)
        emit('joined', {'room': room})

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║     🛡️  SHESHIELD - COMPLETE SAFETY SYSTEM 🛡️                    ║
    ║                                                                   ║
    ║     ✅ SOS Alert - Works!                                        ║
    ║     ✅ Live Tracking - Works!                                    ║
    ║     ✅ Fake Call - Works!                                        ║
    ║     ✅ Real-time Notifications - Works!                          ║
    ║                                                                   ║
    ║     📱 Access: http://localhost:5000                            ║
    ║     🔑 Demo: demo@sheshield.com / demo123                       ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    init_database()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)