# /app/__init__.py
from flask import Flask
from flask_cors import CORS
from .endpoints.groups import groups_bp
from .endpoints.events import events_bp
from .endpoints.users import users_bp
from .endpoints.login import login_bp
from .endpoints.profile import profile_bp
from helpers.dynamodb_helper import DynamoDBHelper
from helpers.mongodb_helper import MongoDBHelper
from helpers.logger import Logger

def create_app():
    app = Flask(__name__)
    CORS(app)

    config = load_config('config.txt')

    # Initialize logger
    logger = Logger(config).get_logger()

    # Register blueprints
    app.register_blueprint(groups_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(login_bp)
    app.register_blueprint(profile_bp)

    if config['DATABASE_TYPE'] == 'dynamoDB':
        db_helper = DynamoDBHelper(config, logger)
    elif config['DATABASE_TYPE'] == 'mongoDB':
        db_helper = MongoDBHelper(config, logger)
    else:
        logger.error('Invalid DATABASE_TYPE specified in config. Please use "dynamoDB" or "mongoDB".')
        return None

    # Store config and db_helper in app's config
    app.config['DB_HELPER'] = db_helper
    app.config['LOGGER'] = logger


    return app

def load_config(config_file):
    config = {}
    with open(config_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config
