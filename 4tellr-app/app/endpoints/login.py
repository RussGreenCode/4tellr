from flask import Flask, request, jsonify, Blueprint, current_app
import bcrypt

login_bp = Blueprint('login', __name__)

# Initialize db_helper at the module level
db_helper = None

@login_bp.before_app_request
def initialize_db_helper():
    global db_helper
    db_helper = current_app.config['DB_HELPER']



@login_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    try:
        user = db_helper.get_user_by_email(email)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'isAuthenticated': True, 'user': user}), 200
        else:
            return jsonify({'isAuthenticated': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@login_bp.route('/api/logout', methods=['POST'])
def logout():
    # Logic to handle session invalidation goes here
    return jsonify({'message': 'Logged out successfully'}), 200
