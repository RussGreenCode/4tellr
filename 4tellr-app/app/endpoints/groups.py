from flask import Flask, request, jsonify, Blueprint, current_app

groups_bp = Blueprint('groups', __name__)

# Initialize db_helper at the module level
db_helper = None

@groups_bp.before_app_request
def initialize_db_helper():
    global db_helper
    db_helper = current_app.config['DB_HELPER']

@groups_bp.route('/api/get_groups', methods=['GET'])
def get_groups():
    try:

        groups = db_helper.get_all_groups()
        return jsonify(groups)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@groups_bp.route('/api/save_group', methods=['POST'])
def save_group():
    try:
        data = request.get_json()
        group_name = data.get('name')
        description = data.get('description')
        events = data.get('events', [])

        if not group_name or not events:
            return jsonify({'error': 'Group name and events are required'}), 400

        items = db_helper.save_group(group_name, events, description)
        return jsonify({'message': 'Group saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@groups_bp.route('/api/delete_group', methods=['POST'])
def delete_group():
    try:
        data = request.get_json()
        group_name = data.get('name')

        if not group_name:
            return jsonify({'error': 'Group name is required'}), 400

        db_helper.delete_group(group_name)

        return jsonify({'message': 'Group deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@groups_bp.route('/api/get_group_details', methods=['POST'])
def get_group_details():
    try:
        data = request.get_json()
        group_name = data.get('name')

        if not group_name:
            return jsonify({'error': 'Group name is required'}), 400

        group = db_helper.get_group_details(group_name)

        if not group:
            return jsonify({'error': 'Group not found'}), 404

        return jsonify(group), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
