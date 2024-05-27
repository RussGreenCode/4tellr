from botocore.exceptions import NoCredentialsError, PartialCredentialsError
from flask import Flask, request, jsonify
from flask_cors import CORS
from helpers.dynamodb_helper import DynamoDBHelper, load_config

app = Flask(__name__)
CORS(app)

config = load_config('config.txt')
db_helper = DynamoDBHelper(config)

@app.route('/')
def hello_world():
    return 'Hello World!'


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

@app.route('/api/events', methods=['POST'])
def create_event():
    data = request.json

    # Basic validation for common fields
    required_fields = [
        'businessDate', 'eventName', 'eventType', 'batchOrRealtime',
        'timestamp', 'eventStatus', 'resource', 'details'
    ]

    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400

    # Specific validation based on event type
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

    else:
        return jsonify({'error': 'Invalid eventType provided'}), 400

    # Insert event into DynamoDB
    try:
        event_id = db_helper.insert_event(data)
    except (NoCredentialsError, PartialCredentialsError):
        return jsonify({'error': 'AWS credentials not configured correctly'}), 500

    return jsonify({'status': 'success', 'event_id': event_id, 'event_data': data}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
