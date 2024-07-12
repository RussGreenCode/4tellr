from flask import Flask, request, jsonify, Blueprint, current_app
import bcrypt

from helpers.user_helper import UserHelper
from helpers.group_helper import GroupHelper

users_bp = Blueprint('users', __name__)

# Initialize db_helper at the module level
db_helper = None


@users_bp.before_app_request
def initialize_helpers():
    global user_helper
    user_helper = UserHelper()
    global group_helper
    group_helper = GroupHelper()

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

            result = user_helper.add_new_user(user)
            results.append(result)

        except Exception as e:
            results.append({'email': email,  'success': False,  'message': str(e)})

    return jsonify(results), 201 if not results else 207


@users_bp.route('/api/delete_user/<string:email>', methods=['DELETE'])
def delete_user(email):
    try:
        response = user_helper.delete_user_by_email(email)
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

        users = user_helper.get_all_users()
        return jsonify(users)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/api/change_password', methods=['POST'])
def change_password():
    data = request.get_json()
    email = data.get('email')
    old_password = data.get('currentPassword')
    new_password = data.get('newPassword')

    if not email or not old_password or not new_password:
        return jsonify({'error': 'Email, old password, and new password are required'}), 400

    try:
        result = user_helper.change_password(email, old_password, new_password)
        if result['success']:
            return jsonify({'success': True, 'message': result['message']}), 200
        else:
            return jsonify({'success': False, 'message': result['message']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/api/get_user', methods=['GET'])
def get_user():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter is required'}), 400

    try:
        user = user_helper.get_user_by_email(email)

        groups = []

        favourite_groups = user.get('favourite_groups')

        if favourite_groups:

            for group_name in favourite_groups:
                group = group_helper.get_group_details(group_name)
                groups.append(group)

        response = {
            'user': user,
            'groups': groups
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/api/save_user_favourite_groups', methods=['POST'])
def save_user_favourite_groups():
    data = request.get_json()
    email = data.get('email')
    favourite_groups = data.get('favourite_groups')

    if not email or favourite_groups is None:
        return jsonify({'error': 'Email and favourite groups are required'}), 400

    try:
        user_helper.save_user_favourite_groups(email, favourite_groups)
        return jsonify({'message': 'Favourite groups updated successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500