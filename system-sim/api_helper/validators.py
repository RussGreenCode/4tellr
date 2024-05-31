class ValidationError(Exception):
    pass

class Validator:
    def validate(self, message):
        raise NotImplementedError("Subclasses must implement this method")

class CommonFieldValidator(Validator):
    required_fields = [
        'businessDate', 'eventName', 'eventType', 'batchOrRealtime',
        'eventTime', 'eventStatus', 'resource', 'details'
    ]

    def validate(self, message):
        for field in self.required_fields:
            if field not in message:
                raise ValidationError(f'{field} is required')

class FileEventValidator(Validator):
    required_fields = ['fileName', 'fileLocation', 'fileSize', 'numberOfRows']

    def validate(self, message):
        if message.get('eventType') == 'File':
            details = message.get('details', {})
            for field in self.required_fields:
                if field not in details:
                    raise ValidationError(f'{field} is required for file-based events')

class MessageEventValidator(Validator):
    required_fields = ['messageId', 'messageQueue']

    def validate(self, message):
        if message.get('eventType') == 'Message':
            details = message.get('details', {})
            for field in self.required_fields:
                if field not in details:
                    raise ValidationError(f'{field} is required for message-based events')

class DatabaseEventValidator(Validator):
    required_fields = ['databaseName', 'tableName', 'operation']

    def validate(self, message):
        if message.get('eventType') == 'Database':
            details = message.get('details', {})
            for field in self.required_fields:
                if field not in details:
                    raise ValidationError(f'{field} is required for database events')
