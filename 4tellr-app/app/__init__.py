# /app/__init__.py
from flask import Flask
from flask_cors import CORS
from .endpoints.groups import groups_bp
from .endpoints.events import events_bp
from helpers.dynamodb_helper import DynamoDBHelper, load_config


def create_app():
    app = Flask(__name__)
    CORS(app)

    # Register blueprints
    app.register_blueprint(groups_bp)
    app.register_blueprint(events_bp)

    config = load_config('config.txt')
    db_helper = DynamoDBHelper(config)

    # Store config and db_helper in app's config
    app.config['DB_HELPER'] = db_helper

    return app