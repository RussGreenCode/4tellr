import requests
from flask import  request, jsonify, jsonify, Blueprint, current_app

from helpers.job_helper import JobHelper
from helpers.job_functions import fetch_url

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.before_app_request
def initialize_db_helper():
    global jobs_helper
    jobs_helper = JobHelper()

@jobs_bp.route('/api/job/calculate_job_length_statistics', methods=['GET'])
def calculate_job_length_statistics():

    business_date = request.args.get('businessDate')

    if not business_date:
        return jsonify({'error': 'business_date parameter is required'}), 400
    try:

        result = jobs_helper.calculate_job_length_statistics(business_date)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/api/jobs', methods=['GET'])
def list_jobs():
    try:
        jobs = current_app.config['SCHEDULER'].get_jobs()
        jobs_info = [{'id': str(job.id),
                      'name': str(job.name),
                      'next_run_time': str(job.next_run_time.isoformat()) if job.next_run_time else 'Paused',
                      'trigger': str(job.trigger),
                      'args': [str(arg) for arg in job.args],
                      'kwargs': {k: str(v) for k, v in job.kwargs.items()}} for job in jobs]
        return jsonify({'success': True, 'data': jobs_info}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@jobs_bp.route('/api/jobs', methods=['POST'])
def create_job():
    job_data = request.json
    job_id = job_data.get('id')
    job_name = job_data.get('name')
    job_trigger = job_data.get('trigger', 'interval')
    job_seconds = job_data.get('seconds', 60)
    job_url = job_data.get('url')
    job_params = job_data.get('params', {})

    if not job_id or not job_name or not job_url:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400

    try:
        current_app.config['SCHEDULER'].add_job(
            id=job_id,
            name=job_name,
            trigger=job_trigger,
            seconds=job_seconds,
            func=fetch_url,
            args=[job_url],
            kwargs={'params': job_params},
            replace_existing=True
        )
        return jsonify({'success': True, 'message': 'Job created successfully'}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@jobs_bp.route('/api/jobs/<job_id>', methods=['DELETE'])
def delete_job(job_id):
    try:
        current_app.config['SCHEDULER'].remove_job(job_id)
        return jsonify({'success': True, 'message': 'Job deleted successfully'}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@jobs_bp.route('/api/jobs/trigger/<job_id>', methods=['POST'])
def trigger_job(job_id):

    override = request.get_json()

    try:
        job = current_app.config['SCHEDULER'].get_job(job_id)
        if not job:
            raise ValueError(f"No job found with ID {job_id}")

        job_func = job.func
        job_args = job.args
        job_kwargs = job.kwargs

        if not override == {}:
            job_kwargs = override

        # Manually trigger the job function with stored args and kwargs
        job_func(*job_args, **job_kwargs)

        current_app.config['LOGGER'].info(f"Job with ID={job_id} triggered successfully")
        return jsonify({'success': True, 'message': 'Job triggered successfully'}), 200
    except Exception as e:
        current_app.config['LOGGER'].error(f"Error triggering job: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@jobs_bp.route('/api/jobs/pause/<job_id>', methods=['POST'])
def pause_job(job_id):
    try:
        current_app.config['SCHEDULER'].pause_job(job_id)
        current_app.config['LOGGER'].info(f"Job with ID={job_id} paused successfully")
        return jsonify({'success': True, 'message': 'Job paused successfully'}), 200
    except Exception as e:
        current_app.config['LOGGER'].error(f"Error pausing job: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@jobs_bp.route('/api/jobs/resume/<job_id>', methods=['POST'])
def resume_job(job_id):
    try:
        current_app.config['SCHEDULER'].resume_job(job_id)
        current_app.config['LOGGER'].info(f"Job with ID={job_id} resumed successfully")
        return jsonify({'success': True, 'message': 'Job resumed successfully'}), 200
    except Exception as e:
        current_app.config['LOGGER'].error(f"Error resuming job: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

