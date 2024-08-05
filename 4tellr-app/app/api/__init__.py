
from fastapi import FastAPI
from app.api.login import router as login_router
from app.api.events import router as events_router
from app.api.users import router as users_router
from app.api.groups import router as groups_router
from app.api.jobs import router as jobs_router

# Import other routers

def register_routes(app: FastAPI):
    app.include_router(login_router)
    app.include_router(events_router)
    app.include_router(users_router)
    app.include_router(groups_router)
    app.include_router(jobs_router)
    # Include other routers
