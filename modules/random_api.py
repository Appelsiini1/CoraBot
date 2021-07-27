import requests
import logging
from constants import RANDOM_API_KEY, REQUEST_LIMITS
from datetime import datetime
from time import sleep

class RandomOrgAPIError(Exception):
    """Exception raised for errors given by the Random.org API.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class RequestLimitReached(Exception):
    """Random.org API request limit reached for the day.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

USAGE_QUERY = {
    "jsonrpc": "2.0",
    "method": "getUsage",
    "params": {
        "apiKey": RANDOM_API_KEY
    },
    "id": 42
}

R_API = "https://api.random.org/json-rpc/4/invoke"

class requestLimits:
    def __init__(self):
        self.bitsLeft = 0 
        self.requestsLeft = 0
        self.advisoryDelay = 0
        self.lastRequest = datetime.today()
        self.updateLimits()

    def updateLimits(self):
        response = requests.post(
            R_API,
            headers={"User-Agent": "Appelsiini1's Discord Bot"},
            json=USAGE_QUERY,
        )

        if response.status_code != 200:
            logging.error(f"Random.org API returned status code {response.status_code}.\nFull response: {response.json()}")
        else:
            json_response = response.json()
            try:
                error_msg = json_response["error"]
                logging.error(f"Random.org API Error: {error_msg}")
                raise RandomOrgAPIError
            except KeyError:
                pass
            result = json_response["result"]
            bitsLeft = result["bitsLeft"]
            requestsLeft = result["requestsLeft"]
            self.bitsLeft = bitsLeft
            self.requestsLeft = requestsLeft

    def checkDelay(self):
        now = datetime.today()
        difference = now - self.lastRequest
        if difference.seconds > self.advisoryDelay:
            sleep(abs(int(difference.seconds)))


    def checkLimits(self):
        # Raise error if limit is reached
        if self.bitsLeft <= 15 or self.requestsLeft == 0:
            raise RequestLimitReached

    def resetLimits(self):
        self.requestsLeft = 1000
        self.bitsLeft = 250000


def makeRequest(n: int, min: int, max: int, id=42):
    
    query = {
    "jsonrpc": "2.0",
    "method": "generateIntegers",
    "params": {
        "apiKey": RANDOM_API_KEY,
        "n": n,
        "min": min,
        "max": max,
        "replacement": False
        },
    "id": id
    }

    REQUEST_LIMITS.checkLimits()
    REQUEST_LIMITS.checkDelay()

    response = requests.post(
    R_API,
    headers={"User-Agent": "Appelsiini1's Discord Bot"},
    json=query,
    )

    if response.status_code != 200:
        logging.error(f"Random.org API returned status code {response.status_code}.\nFull response: {response.json()}")
    else:
        json_response = response.json()
        try:
            error_msg = json_response["error"]
            logging.error(f"Random.org API Error: {error_msg}")
            raise RandomOrgAPIError
        except KeyError:
            pass
        result = json_response["result"]["random"]["data"]
        REQUEST_LIMITS.advisoryDelay = json_response["result"]["advisoryDelay"]/1000
        REQUEST_LIMITS.lastRequest = datetime.today()

        return result
