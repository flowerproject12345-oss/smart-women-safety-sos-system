"""
🔐 Authentication Routes
"""

from flask import Blueprint, request, jsonify, session
from models.user import User
from database.database import get_db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register new user"""
    data = request.json
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    full_name = data.get('full_name')
    
    # Check if user exists
    if User.find_by_username(username):
        return jsonify({'success': False, 'message': 'Username already exists'}), 400
    
    if User.find_by_email(email):
        return jsonify({'success': False, 'message': 'Email already exists'}), 400
    
    # Create user
    user_id = User.create(username, email, phone, password, full_name)
    
    return jsonify({
        'success': True,
        'message': 'Registration successful!',
        'user_id': user_id
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user = User.authenticate(username, password)
    
    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['full_name'] = user['full_name']
        
        # Update last login
        User.update_last_login(user['id'])
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'full_name': user['full_name']
            }
        })
    else:
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Get current logged in user"""
    if 'user_id' in session:
        user = User.find_by_id(session['user_id'])
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'phone': user['phone']
                }
            })
    
    return jsonify({'success': False, 'message': 'Not logged in'}), 401