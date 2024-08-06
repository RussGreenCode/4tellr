import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_url(url, params, timeout=10):
    try:
        logger.info(f"Fetching URL: {url} with params: {params}")
        attributes = params['params'] if 'params' in params else {}

        response = requests.get(url, params=attributes, timeout=timeout)

        logger.info(f"Response status code: {response.status_code}")

        # Check if the response status code indicates success
        if response.status_code == 200:
            logger.info("Successfully fetched the URL.")
            return response.json()  # or response.text depending on the expected response
        else:
            logger.error(f"Failed to fetch URL. Status code: {response.status_code}")
            return None

    except requests.exceptions.Timeout:
        logger.error("Request timed out")
        raise

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching URL: {e}")
        raise
