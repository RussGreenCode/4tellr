from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


app.route('/api/events', methods=['POST'])

@app.route('/api/events', methods=['POST'])
def ceate_event():
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

    elif event_type == 'Message':
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

    # Here you would typically save the event to a database
    # For demonstration, we're just returning the data
    event_id = datetime.now().strftime('%Y%m%d%H%M%S')  # Simulating an event ID

    print(data)

    return jsonify({'status': 'success', 'event_id': event_id, 'event_data': data}), 201

if __name__ == '__main__':
    app.run()
