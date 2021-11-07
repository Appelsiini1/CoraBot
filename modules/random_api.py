import requests
import logging
from constants import RANDOM_API_KEY, REQUEST_LIMITS, R_API
from datetime import datetime
from modules.custom_errors import RandomOrgAPIError


def makeRequest(n: int, min: int, max: int, id=42):

    query = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": RANDOM_API_KEY,
            "n": n,
            "min": min,
            "max": max,
            "replacement": False,
        },
        "id": id,
    }

    response = requests.post(
        R_API,
        headers={"User-Agent": "Appelsiini1's Discord Bot"},
        json=query,
    )

    if response.status_code != 200:
        logging.error(
            f"Random.org API returned status code {response.status_code}.\nFull response: {response.json()}"
        )
    else:
        json_response = response.json()
        try:
            error_msg = json_response["error"]
            logging.error(f"Random.org API Error: {error_msg}")
            raise RandomOrgAPIError(error_msg)
        except KeyError:
            pass
        result = json_response["result"]["random"]["data"]
        REQUEST_LIMITS.advisoryDelay = json_response["result"]["advisoryDelay"] / 1000
        REQUEST_LIMITS.lastRequest = datetime.today()

        return result


def randInt(n: int, min: int, max: int, id=42):
    """Get n random integers between min and max. Includes both endpoints.
    n cannot be 0 or negative.
    Always returns a list."""

    if n <= 0:
        raise ValueError
    REQUEST_LIMITS.checkLimits()
    REQUEST_LIMITS.checkDelay()
    result = makeRequest(n, min, max, id)
    
    return result