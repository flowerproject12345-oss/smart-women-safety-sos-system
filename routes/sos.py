"""
🚨 SOS Routes
"""

from flask import Blueprint, request, jsonify, session
from models.sos_alert import SOSAlert
from models.contact import EmergencyContact
from models.user import User
from services.sms_service import send_sms_alert
from services.location_service import get_address_from_coordinates
from database.database import get_db
from datetime import datetime
import json

sos_bp = Blueprint('sos', __name__)

@sos_bp.route('/trigger', methods=['POST'])
def trigger_sos():
    """Trigger SOS alert"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    data = request.json
    latitude = data.get('latitude', 13.0827)
    longitude = data.get('longitude', 80.2707)
    address = data.get('address', '')
    
    # Get address if not provided
    if not address:
        address = get_address_from_coordinates(latitude, longitude)
    
    # Create SOS alert
    sos_id = SOSAlert.create(session['user_id'], latitude, longitude, address)
    
    # Get user details
    user = User.find_by_id(session['user_id'])
    
    # Get emergency contacts
    contacts = EmergencyContact.get_all(session['user_id'])
    
    # Send alerts to all contacts
    alerts_sent = []
    for contact in contacts:
        # Send SMS
        if contact['phone']:
            sms_sent = send_sms_alert(
                contact['phone'],
                user['full_name'] or user['username'],
                latitude,
                longitude,
                address
            )
            if sms_sent:
                alerts_sent.append(f"📱 SMS to {contact['name']}")
        
        # Send Email (if email exists and we have email service)
        if contact.get('email'):
            from services.email_service import send_email_alert
            email_sent = send_email_alert(
                contact['email'],
                user['full_name'] or user['username'],
                latitude,
                longitude,
                address
            )
            if email_sent:
                alerts_sent.append(f"📧 Email to {contact['name']}")
    
    # Log action
    conn = get_db()
    conn.execute("""
        INSERT INTO action_history (user_id, action_type, action_details)
        VALUES (?, ?, ?)
    """, (session['user_id'], 'sos_triggered', json.dumps({
        'sos_id': sos_id,
        'latitude': latitude,
        'longitude': longitude,
        'address': address
    })))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': '🚨 SOS Alert Triggered Successfully!',
        'sos_id': sos_id,
        'latitude': latitude,
        'longitude': longitude,
        'address': address,
        'alerts_sent': alerts_sent,
        'contacts_notified': len(contacts)
    })

@sos_bp.route('/recent', methods=['GET'])
def get_recent_sos():
    """Get recent SOS alerts"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    alerts = SOSAlert.get_all(session['user_id'], limit=50)
    return jsonify(alerts)

@sos_bp.route('/active', methods=['GET'])
def get_active_sos():
    """Get active SOS alerts"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    alerts = SOSAlert.get_active(session['user_id'])
    return jsonify(alerts)

@sos_bp.route('/resolve/<int:sos_id>', methods=['POST'])
def resolve_sos(sos_id):
    """Resolve SOS alert"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    SOSAlert.resolve(sos_id, session['user_id'])
    
    # Log action
    conn = get_db()
    conn.execute("""
        INSERT INTO action_history (user_id, action_type, action_details)
        VALUES (?, ?, ?)
    """, (session['user_id'], 'sos_resolved', json.dumps({'sos_id': sos_id})))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': '✅ SOS alert resolved'
    })

@sos_bp.route('/stats', methods=['GET'])
def get_sos_stats():
    """Get SOS statistics"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    stats = SOSAlert.get_stats(session['user_id'])
    return jsonify(stats)