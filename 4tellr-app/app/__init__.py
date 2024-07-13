from datetime import datetime
import requests
from flask import Flask
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from .endpoints.groups import groups_bp
from .endpoints.events import events_bp
from .endpoints.users import users_bp
from .endpoints.login import login_bp
from .endpoints.profile import profile_bp
from .endpoints.jobs import jobs_bp
from helpers.dynamodb_helper import DynamoDBHelper
from helpers.mongodb_helper import MongoDBHelper
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
import atexit
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
    app.register_blueprint(jobs_bp)

    if config['DATABASE_TYPE'] == 'dynamoDB':
        db_helper = DynamoDBHelper(config, logger)

    elif config['DATABASE_TYPE'] == 'mongoDB':
        db_helper = MongoDBHelper(config, logger)
        jobstores = {
            'default': MongoDBJobStore(database='4tellr', collection='jobs', client=db_helper.client)
        }
    else:
        logger.error('Invalid DATABASE_TYPE specified in config. Please use "dynamoDB" or "mongoDB".')
        return None

    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone='UTC')
    scheduler.start()

    # Store config and db_helper in app's config
    app.config['DB_HELPER'] = db_helper
    app.config['LOGGER'] = logger
    app.config['SCHEDULER'] = scheduler

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())

    return app


def setup_scheduler(app):
    scheduler = BackgroundScheduler()

    def trigger_job():
        url = 'http://127.0.0.1:5000/api/job/calculate_job_length_statistics'
        try:
            response = requests.get(url, params={'businessDate': datetime.now().strftime('%Y-%m-%d')})
            if response.status_code == 200:
                app.logger.info("Job length statistics calculated successfully.")
            else:
                app.logger.error(f"Failed to calculate job length statistics: {response.json()}")
        except requests.RequestException as e:
            app.logger.error(f"Error triggering job length statistics: {e}")

    scheduler.add_job(trigger_job, 'cron', hour=0)  # Adjust the schedule as needed
    scheduler.start()

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


def load_config(config_file):
    config = {}
    with open(config_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            config[key] = value
    return config
