import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_url(url, params):
    try:
        logger.info(f"Fetching URL: {url} with params: {params}")
        response = requests.get(url, params=params)
        logger.info(f"Response status code: {response.status_code}")
        return response.json()  # or response.text depending on the expected response
    except Exception as e:
        logger.error(f"Error fetching URL: {e}")
        raise
