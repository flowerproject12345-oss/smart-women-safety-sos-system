"""
📍 Live Tracking Routes
"""

from flask import Blueprint, request, jsonify, session
from models.tracking import TrackingSession
from models.location import LocationHistory
from services.location_service import get_address_from_coordinates, check_safe_zone_proximity
from database.database import get_db
import secrets
import json

tracking_bp = Blueprint('tracking', __name__)

# Store active tracking sessions in memory
active_tracking = {}

@tracking_bp.route('/start', methods=['POST'])
def start_tracking():
    """Start live tracking session"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    session_id = secrets.token_hex(16)
    TrackingSession.create(session['user_id'], session_id)
    
    active_tracking[session['user_id']] = session_id
    
    return jsonify({
        'success': True,
        'message': '📍 Live tracking started',
        'session_id': session_id,
        'share_link': f"/share/track/{session_id}"
    })

@tracking_bp.route('/stop', methods=['POST'])
def stop_tracking():
    """Stop live tracking session"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    TrackingSession.stop(session['user_id'])
    
    if session['user_id'] in active_tracking:
        del active_tracking[session['user_id']]
    
    return jsonify({
        'success': True,
        'message': '⏹️ Live tracking stopped'
    })

@tracking_bp.route('/status', methods=['GET'])
def tracking_status():
    """Get tracking status"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    is_tracking = session['user_id'] in active_tracking
    
    return jsonify({
        'is_tracking': is_tracking,
        'session_id': active_tracking.get(session['user_id'])
    })

@tracking_bp.route('/update-location', methods=['POST'])
def update_location():
    """Update current location"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    data = request.json
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    accuracy = data.get('accuracy')
    
    if not latitude or not longitude:
        return jsonify({'success': False, 'message': 'Coordinates required'}), 400
    
    # Get address
    address = get_address_from_coordinates(latitude, longitude)
    
    # Check safe zones
    safe_zone_alerts = check_safe_zone_proximity(session['user_id'], latitude, longitude)
    
    # Save location if tracking active
    if session['user_id'] in active_tracking:
        session_id = active_tracking[session['user_id']]
        LocationHistory.create(session['user_id'], session_id, latitude, longitude, address, accuracy)
    
    return jsonify({
        'success': True,
        'address': address,
        'safe_zone_alerts': safe_zone_alerts
    })