import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import atexit
from app.api import register_routes
from helpers.dynamodb_helper import DynamoDBHelper
from helpers.mongodb_helper import MongoDBHelper
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.mongodb import MongoDBJobStore
from core.logging import Logger
from app.middleware import LogRequestMiddleware  # Import the middleware


def create_app():
    app = FastAPI()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )


    config = load_config('../config.txt')

    # Add log request middleware
    if config['LOG_LEVEL'] == 'DEBUG':
        app.add_middleware(LogRequestMiddleware)

    # Initialize logger
    logger = Logger(config).get_logger()

    # Register routes
    register_routes(app)

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

    # Store config and db_helper in app's state
    app.state.DB_HELPER = db_helper
    app.state.LOGGER = logger
    app.state.SCHEDULER = scheduler

    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())



    return app


def setup_scheduler(app):
    scheduler = BackgroundScheduler()
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


app = create_app()

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
