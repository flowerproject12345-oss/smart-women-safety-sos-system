"""
🏠 Safe Zones Routes
"""

from flask import Blueprint, request, jsonify, session
from models.safe_zone import SafeZone
from database.database import get_db
import json

safezones_bp = Blueprint('safezones', __name__)

@safezones_bp.route('/get', methods=['GET'])
def get_safe_zones():
    """Get all safe zones"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    zones = SafeZone.get_all(session['user_id'])
    return jsonify(zones)

@safezones_bp.route('/add', methods=['POST'])
def add_safe_zone():
    """Add new safe zone"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    data = request.json
    name = data.get('name')
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    address = data.get('address')
    radius = data.get('radius', 100)
    
    if not name or not latitude or not longitude:
        return jsonify({'success': False, 'message': 'Name and location required'}), 400
    
    zone_id = SafeZone.create(session['user_id'], name, latitude, longitude, address, radius)
    
    # Log action
    conn = get_db()
    conn.execute("""
        INSERT INTO action_history (user_id, action_type, action_details)
        VALUES (?, ?, ?)
    """, (session['user_id'], 'safe_zone_added', json.dumps({
        'zone_id': zone_id,
        'name': name,
        'latitude': latitude,
        'longitude': longitude
    })))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'✅ {name} added as safe zone',
        'zone_id': zone_id
    })

@safezones_bp.route('/delete/<int:zone_id>', methods=['DELETE'])
def delete_safe_zone(zone_id):
    """Delete safe zone"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    SafeZone.delete(zone_id, session['user_id'])
    
    return jsonify({
        'success': True,
        'message': '✅ Safe zone deleted successfully'
    })

@safezones_bp.route('/check-proximity', methods=['POST'])
def check_proximity():
    """Check proximity to safe zones"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    if not latitude or not longitude:
        return jsonify({'success': False, 'message': 'Coordinates required'}), 400
    
    alerts = SafeZone.check_proximity(session['user_id'], latitude, longitude)
    
    return jsonify({
        'success': True,
        'alerts': alerts
    })