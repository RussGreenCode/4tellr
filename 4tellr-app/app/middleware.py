from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import logging
import json
from starlette.datastructures import FormData


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log the request details
        logging.info(f"Request: {request.method} {request.url}")

        try:
            body = await request.body()
            if body:
                logging.info(f"Request body: {body.decode()}")

            # Recreate the request with the original body so downstream handlers can still access it
            request = Request(request.scope,
                              receive=lambda: ({"type": "http.request", "body": body, "more_body": False}))

        except Exception as e:
            logging.error(f"Error reading request body: {e}")

        response = await call_next(request)

        # Log the response details
        logging.info(f"Response status: {response.status_code}")

        return response
