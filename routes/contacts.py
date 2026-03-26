"""
👥 Emergency Contacts Routes
"""

from flask import Blueprint, request, jsonify, session
from models.contact import EmergencyContact
from database.database import get_db
import json

contacts_bp = Blueprint('contacts', __name__)

@contacts_bp.route('/get', methods=['GET'])
def get_contacts():
    """Get all emergency contacts"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    contacts = EmergencyContact.get_all(session['user_id'])
    return jsonify(contacts)

@contacts_bp.route('/add', methods=['POST'])
def add_contact():
    """Add new emergency contact"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    relationship = data.get('relationship')
    is_primary = data.get('is_primary', False)
    
    if not name or not phone:
        return jsonify({'success': False, 'message': 'Name and phone are required'}), 400
    
    contact_id = EmergencyContact.create(
        session['user_id'], name, phone, email, relationship, is_primary
    )
    
    # Log action
    conn = get_db()
    conn.execute("""
        INSERT INTO action_history (user_id, action_type, action_details)
        VALUES (?, ?, ?)
    """, (session['user_id'], 'contact_added', json.dumps({
        'contact_id': contact_id,
        'name': name,
        'phone': phone
    })))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'✅ {name} added as emergency contact',
        'contact_id': contact_id
    })

@contacts_bp.route('/delete/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    """Delete emergency contact"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    EmergencyContact.delete(contact_id, session['user_id'])
    
    # Log action
    conn = get_db()
    conn.execute("""
        INSERT INTO action_history (user_id, action_type, action_details)
        VALUES (?, ?, ?)
    """, (session['user_id'], 'contact_deleted', json.dumps({'contact_id': contact_id})))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': '✅ Contact deleted successfully'
    })

@contacts_bp.route('/update/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    """Update emergency contact"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'}), 401
    
    data = request.json
    EmergencyContact.update(contact_id, session['user_id'], **data)
    
    return jsonify({
        'success': True,
        'message': '✅ Contact updated successfully'
    })