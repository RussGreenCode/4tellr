from flask import Flask, request, jsonify, Blueprint, current_app
import bcrypt

users_bp = Blueprint('users', __name__)

# Initialize db_helper at the module level
db_helper = None


@users_bp.before_app_request
def initialize_db_helper():
    global db_helper
    db_helper = current_app.config['DB_HELPER']


@users_bp.route('/api/add_users', methods=['POST'])
def add_users():
    data = request.get_json()
    emails = data.get('emails', [])
    if not emails:
        return jsonify({'error': 'Emails are required'}), 400

    users = []
    results = []
    for email in emails:
        password = bcrypt.hashpw('dummy_password'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        user = {
            'email': email,
            'password': password
        }
        try:

            result = db_helper.add_user(user)
            results.append(result)

        except Exception as e:
            results.append({'email': email,  'success': False,  'message': str(e)})

    return jsonify(results), 201 if not results else 207


@users_bp.route('/api/delete_user/<string:email>', methods=['DELETE'])
def delete_user(email):
    try:
        response = db_helper.delete_user_by_email(email)
        results = []
        if response:
            results.append({'email': email, 'success': True, 'message': f'User with email {email} deleted successfully.'})
        else:
            results.append({'email': email, 'success': False, 'message': f'User with email {email} failed to delete.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify(results), 200

@users_bp.route('/api/get_users', methods=['GET'])
def get_users():
    try:

        users = db_helper.get_all_users()
        return jsonify(users)

    except Exception as e:
        return jsonify({'error': str(e)}), 500