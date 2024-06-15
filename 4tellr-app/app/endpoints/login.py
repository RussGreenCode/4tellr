from flask import Flask, request, jsonify, Blueprint, current_app

login_bp = Blueprint('login', __name__)

# Initialize db_helper at the module level
db_helper = None

@login_bp.before_app_request
def initialize_db_helper():
    global db_helper
    db_helper = current_app.config['DB_HELPER']

