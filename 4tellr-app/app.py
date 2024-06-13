import datetime
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import Flask, request, jsonify
from flask_cors import CORS
from helpers.dynamodb_helper import DynamoDBHelper, load_config

app = Flask(__name__)
CORS(app)

config = load_config('config.txt')
db_helper = DynamoDBHelper(config)


@app.route('/api/events', methods=['GET'])
def get_events_by_date():
    business_date = request.args.get('businessDate')
    if not business_date:
        return jsonify({'error': 'businessDate parameter is required'}), 400

    try:
        events = db_helper.query_events_by_date(business_date)
        return jsonify(events), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart_data', methods=['GET'])
def get_events_by_date_for_chart():
    business_date = request.args.get('businessDate')
    if not business_date:
        return jsonify({'error': 'businessDate parameter is required'}), 400

    try:
        events = db_helper.query_events_by_date_for_chart(business_date)
        return jsonify(events), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/event_details', methods=['GET'])
def get_event_details():
    event_name = request.args.get('eventName')
    event_status = request.args.get('eventStatus')

    if not event_name or not event_status:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        data = db_helper.get_monthly_events(event_name, event_status)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json

    required_fields = [
        'businessDate', 'eventName', 'eventType', 'batchOrRealtime',
        'eventTime', 'eventStatus', 'resource', 'details'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    event_type = data.get('eventType')
    details = data.get('details', {})

    if event_type == 'FILE':
        file_fields = ['fileName', 'fileLocation', 'fileSize', 'numberOfRows']
        for field in file_fields:
            if field not in details:
                return jsonify({'error': f'{field} is required for file-based events'}), 400

    elif event_type == 'MESSAGE':
        message_fields = ['messageId', 'messageQueue']
        for field in message_fields:
            if field not in details:
                return jsonify({'error': f'{field} is required for message-based events'}), 400

    elif event_type == 'DATABASE':
        db_fields = ['databaseName', 'tableName', 'operation']
        for field in db_fields:
            if field not in details:
                return jsonify({'error': f'{field} is required for database events'}), 400
    elif event_type == 'PROCESS':
        db_fields = ['databaseName', 'tableName', 'operation']

    else:
        return jsonify({'error': 'Invalid eventType provided'}), 400

    try:
        event_id = db_helper.insert_event(data)
    except (NoCredentialsError, PartialCredentialsError):
        return jsonify({'error': 'AWS credentials not configured correctly'}), 500

    return jsonify({'status': 'success', 'event_id': event_id, 'event_data': data}), 201


@app.route('/api/events/<string:business_date>/<string:event_name>', methods=['GET'])
def get_event(business_date, event_name):
    try:
        events = db_helper.query_events_by_date(business_date)
        event = next((e for e in events if e['eventName'] == event_name), None)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        return jsonify(event), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/generate-expectations', methods=['POST'])
def generate_expectations():
    data = request.json
    required_fields = ['businessDate']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    business_date = data['businessDate']

    try:
        # Delete existing expectations for the given business date
        db_helper.delete_expectations_for_business_date(business_date)

        # DGenerate the new expectations for that business date
        expectations = db_helper.generate_expectations(business_date)
        if not expectations:
            return jsonify({'error': 'Unable to generate expectations, no metrics found.'}), 404
        return jsonify(expectations), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/delete_events', methods=['POST'])
def delete_events():
    data = request.json
    required_fields = ['businessDates']

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    business_dates = data['businessDates']

    if not isinstance(business_dates, list):
        return jsonify({'error': 'businessDates must be a list'}), 400

    try:
        # Delete existing events for the given business dates
        db_helper.delete_events_for_business_dates(business_dates)

        return jsonify("Events deleted successfully"), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/latest-metrics', methods=['GET'])
def get_latest_metrics():
    try:
        latest_metrics = db_helper.get_latest_metrics()
        return jsonify(latest_metrics), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/expected-times/update', methods=['POST'])
def update_expected_times():
    try:
        db_helper.update_expected_times()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/events/<string:event_name>/<string:event_status>/expected-time', methods=['GET'])
def get_expected_time(event_name, event_status):
    try:
        expected_time = db_helper.get_expected_time(event_name, event_status)
        if not expected_time:
            return jsonify({'error': 'Expected time not found'}), 404
        return jsonify(expected_time), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_expectation_list', methods=['GET'])
def get_expectation_list():
    try:
        items = db_helper.get_expectation_list()
        return jsonify(items)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/get_groups', methods=['GET'])
def get_groups():
    try:

        groups = db_helper.get_all_groups()
        return jsonify(groups)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/save_group', methods=['POST'])
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


@app.route('/api/delete_group', methods=['POST'])
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


@app.route('/api/get_group_details', methods=['POST'])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
