from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel
from typing import List
from services.alert_services import AlertServices


router = APIRouter()


def get_alert_services(request: Request):
    return AlertServices(request.app.state.DB_HELPER, request.app.state.LOGGER)


class AlertData(BaseModel):
    alert_name: str
    description: str
    group_name: str



@router.post("/api/alerts")
async def save_alert(data: AlertData, alert_services: AlertServices = Depends(get_alert_services)):
    try:
        response = alert_services.save_alert(data.alert_name, data.description, data.group_name)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/alerts")
async def get_all_alerts(alert_services: AlertServices = Depends(get_alert_services)):
    try:
        alerts = alert_services.get_all_alerts()
        return alerts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/alerts")
async def delete_alert(alert_name: str, alert_services: AlertServices = Depends(get_alert_services)):
    try:
        response = alert_services.delete_alert(alert_name)
        return response['message']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/api/alerts")
async def update_alert(data: AlertData, alert_services: AlertServices = Depends(get_alert_services)):
    try:
        response = alert_services.update_alert(data.alert_name, data.description, data.group_name)
        return response['message']
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))