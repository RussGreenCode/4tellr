from fastapi import APIRouter, HTTPException, Request, Depends, Query
from pydantic import BaseModel
from services.event_services import EventServices

router = APIRouter()

def get_event_helper(request: Request):
    return EventServices(request.app.state.DB_HELPER, request.app.state.LOGGER)

class EventData(BaseModel):
    businessDate: str
    eventName: str
    eventType: str
    batchOrRealtime: str
    eventTime: str
    eventStatus: str
    resource: str
    details: dict

class BusinessDateRequest(BaseModel):
    businessDate: str

class BusinessDatesRequest(BaseModel):
    businessDates: list[str]

class EventRequest(BaseModel):
    event_name: str
    event_status: str
    business_date: str


@router.get('/api/events')
async def get_events_by_date(business_date: str, event_helper: EventServices = Depends(get_event_helper)):
    if not business_date:
        raise HTTPException(status_code=400, detail='business_date parameter is required')
    try:
        events = event_helper.query_events_by_date(business_date)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/event')
async def get_event_info_by_date(
    event_name: str = Query(..., alias="event_name"),
    event_status: str = Query(..., alias="event_status"),
    business_date: str = Query(..., alias="business_date"),
    event_helper: EventServices = Depends(get_event_helper)
):
    if not business_date:
        raise HTTPException(status_code=400, detail='business_date parameter is required')
    try:
        events = event_helper.get_event_info_by_date(event_name, event_status, business_date)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/chart_data')
async def get_events_by_date_for_chart(business_date: str, event_helper: EventServices = Depends(get_event_helper)):
    if not business_date:
        raise HTTPException(status_code=400, detail='business_date parameter is required')
    try:
        events = event_helper.query_events_by_date_for_chart(business_date)
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/chart_data_monthly_summary')
async def get_events_for_chart_by_month(year: int = Query(...), month: int = Query(...), event_helper: EventServices = Depends(get_event_helper)):
    try:
        summary = event_helper.get_events_for_chart_by_month(year, month)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/api/event_details')
async def get_event_details(event_name: str, event_status: str, event_helper: EventServices = Depends(get_event_helper)):
    if not event_name or not event_status:
        raise HTTPException(status_code=400, detail='Missing required parameters')
    try:
        data = event_helper.get_monthly_events(event_name, event_status)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/api/events')
async def create_event(data: EventData, event_helper: EventServices = Depends(get_event_helper)):
    required_fields = [
        'businessDate', 'eventName', 'eventType', 'batchOrRealtime',
        'eventTime', 'eventStatus', 'resource', 'details'
    ]
    for field in required_fields:
        if field not in data.dict():
            raise HTTPException(status_code=400, detail=f'{field} is required')

    event_type = data.eventType
    details = data.details
    status = data.eventStatus

    if status == 'ERROR':
        db_fields = ['error_code', 'error_description']
    elif event_type == 'FILE':
        file_fields = ['fileName', 'fileLocation', 'fileSize', 'numberOfRows']
        for field in file_fields:
            if field not in details:
                raise HTTPException(status_code=400, detail=f'{field} is required for file-based events')
    elif event_type == 'MESSAGE':
        message_fields = ['messageId', 'messageQueue']
        for field in message_fields:
            if field not in details:
                raise HTTPException(status_code=400, detail=f'{field} is required for message-based events')
    elif event_type == 'DATABASE':
        db_fields = ['databaseName', 'tableName', 'operation']
        for field in db_fields:
            if field not in details:
                raise HTTPException(status_code=400, detail=f'{field} is required for database events')
    elif event_type == 'PROCESS':
        db_fields = ['process_id', 'process_name']
    else:
        raise HTTPException(status_code=400, detail='Invalid eventType provided')

    try:
        event_id = event_helper.insert_event(data.dict())
        return {'status': 'success', 'event_id': event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail='AWS credentials not configured correctly')

@router.post('/api/events/generate-expectations')
async def generate_expectations(data: BusinessDateRequest, event_helper: EventServices = Depends(get_event_helper)):
    business_date = data.businessDate
    try:
        event_helper.delete_expectations_for_business_date(business_date)
        result = event_helper.generate_expectations(business_date)
        if not result:
            raise HTTPException(status_code=404, detail='Unable to generate expectations, no metrics found.')
        return {'status': 'Success'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/api/events/delete_events')
async def delete_events(data: BusinessDatesRequest, event_helper: EventServices = Depends(get_event_helper)):
    business_dates = data.businessDates
    if not isinstance(business_dates, list):
        raise HTTPException(status_code=400, detail='businessDates must be a list')
    try:
        event_helper.delete_events_for_business_dates(business_dates)
        return "Events deleted successfully"
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post('/api/events/expected-times/update')
async def update_expected_times(event_helper: EventServices = Depends(get_event_helper)):
    try:
        event_helper.update_expected_times()
        return {'status': 'success'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/get_expectation_list')
async def get_expectation_list(event_helper: EventServices = Depends(get_event_helper)):
    try:
        items = event_helper.get_expectation_list()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/event/event_metadata_list')
async def event_metadata_list(event_helper: EventServices = Depends(get_event_helper)):
    try:
        items = event_helper.event_metadata_list()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/process/get_process_statistics_list')
async def get_process_stats_list(business_date: str, event_helper: EventServices = Depends(get_event_helper)):

    try:
        items = event_helper.get_process_stats_list(business_date)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/process/get_process_statistics')
async def get_process_statistics(event_name: str, event_helper: EventServices = Depends(get_event_helper)):
    try:
        items = event_helper.get_process_by_name(event_name)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/api/event/get_event_metadata')
async def get_event_metadata(id: str, event_helper: EventServices = Depends(get_event_helper)):
    try:
        items = event_helper.get_event_metadata(id)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put('/api/event/event_metadata')
async def save_event_metadata(data: dict, event_helper: EventServices = Depends(get_event_helper)):
    required_fields = ['expectation_time']
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f'{field} is required')
    try:
        items = event_helper.save_event_metadata(data)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put('/api/event/event_metadata_dependencies')
async def save_event_metadata_dependencies(data: dict, event_helper: EventServices = Depends(get_event_helper)):
    required_fields = ['dependencies']
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f'{field} is required')
    try:
        items = event_helper.update_metadata_with_dependencies(data)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/api/event/create_daily_occurrences')
async def create_daily_occurrences_from_statistics(data: dict, event_helper: EventServices = Depends(get_event_helper)):

    try:
        items = event_helper.create_daily_occurrences_from_statistics(data)
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))