import requests
from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from services.job_services import JobServices
from services.event_services import EventServices
from helpers.job_functions import fetch_url

router = APIRouter()

class JobCreateRequest(BaseModel):
    id: str
    name: str
    trigger: str = 'interval'
    seconds: int = 60
    url: str
    params: dict = {}


def get_job_helper(request: Request):
    return JobServices(request.app.state.DB_HELPER, request.app.state.LOGGER)

def get_event_helper(request: Request):
    return EventServices(request.app.state.DB_HELPER, request.app.state.LOGGER)


@router.get("/api/job/calculate_job_length_statistics")
async def calculate_job_length_statistics(businessDate: str, request: Request, jobs_helper: JobServices = Depends(get_job_helper)):
    if not businessDate:
        raise HTTPException(status_code=400, detail="business_date parameter is required")

    try:
        jobs_helper.delete_processes_for_date(businessDate)
        result = jobs_helper.calculate_job_length_statistics(businessDate)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/job/create_event_metadata_from_events")
async def create_event_metadata_from_events(businessDate: str, request: Request, event_helper: EventServices = Depends(get_event_helper)):

    if not businessDate:
        raise HTTPException(status_code=400, detail="business_date parameter is required")

    try:
        result = event_helper.create_event_metadata_from_events(businessDate)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/jobs")
async def list_jobs(request: Request):
    try:
        jobs = request.app.state.SCHEDULER.get_jobs()
        jobs_info = [{'id': str(job.id),
                      'name': str(job.name),
                      'next_run_time': str(job.next_run_time.isoformat()) if job.next_run_time else 'Paused',
                      'trigger': str(job.trigger),
                      'args': [str(arg) for arg in job.args],
                      'kwargs': {k: str(v) for k, v in job.kwargs.items()}} for job in jobs]
        return {'success': True, 'data': jobs_info}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/jobs")
async def create_job(job_data: JobCreateRequest, request: Request):
    job_id = job_data.id
    job_name = job_data.name
    job_trigger = job_data.trigger
    job_seconds = job_data.seconds
    job_url = job_data.url
    job_params = job_data.params

    if not job_id or not job_name or not job_url:
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        request.app.state.SCHEDULER.add_job(
            id=job_id,
            name=job_name,
            trigger=job_trigger,
            seconds=job_seconds,
            func=fetch_url,
            args=[job_url],
            kwargs={'params': job_params},
            replace_existing=True
        )
        return {'success': True, 'message': 'Job created successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, request: Request):
    try:
        request.app.state.SCHEDULER.remove_job(job_id)
        return {'success': True, 'message': 'Job deleted successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/jobs/trigger/{job_id}")
async def trigger_job(job_id: str, request: Request, override: dict = None):
    override = override or {}

    try:
        job = request.app.state.SCHEDULER.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail=f"No job found with ID {job_id}")

        job_func = job.func
        job_args = job.args
        job_kwargs = job.kwargs

        if override:
            job_kwargs = override

        job_func(*job_args, **job_kwargs)
        request.app.state.LOGGER.info(f"Job with ID={job_id} triggered successfully")
        return {'success': True, 'message': 'Job triggered successfully'}
    except Exception as e:
        request.app.state.LOGGER.error(f"Error triggering job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/jobs/pause/{job_id}")
async def pause_job(job_id: str, request: Request):
    try:
        request.app.state.SCHEDULER.pause_job(job_id)
        request.app.state.LOGGER.info(f"Job with ID={job_id} paused successfully")
        return {'success': True, 'message': 'Job paused successfully'}
    except Exception as e:
        request.app.state.LOGGER.error(f"Error pausing job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/jobs/resume/{job_id}")
async def resume_job(job_id: str, request: Request):
    try:
        request.app.state.SCHEDULER.resume_job(job_id)
        request.app.state.LOGGER.info(f"Job with ID={job_id} resumed successfully")
        return {'success': True, 'message': 'Job resumed successfully'}
    except Exception as e:
        request.app.state.LOGGER.error(f"Error resuming job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
