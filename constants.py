import os
import logging
import sqlite3

from sys import exit
from discord import Intents, Game
from requests import post
from modules.custom_errors import RandomOrgAPIError, RequestLimitReached
from datetime import datetime
from time import sleep


def get_tokens():
    """Gets environment variables. Returns a list."""
    try:
        with open(".env", "r") as f:
            tokens = f.readlines()
    except Exception:
        logging.exception("Could not acquire environment variables. Stopping.")
        exit(1)
    return tokens


# Functional constants
PREFIX = "!c "
DB_F = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "Databases", "database.db"
)
INTENTS = Intents().all()
ACTIVITY = Game("!c help")

# Token constants
TOKENS = get_tokens()
DISCORD_TOKEN = TOKENS[0].lstrip("TOKEN").strip()[1:]
TWIT_API_KEY = TOKENS[1].lstrip("API_KEY").strip()[1:]
TWIT_API_SECRET = TOKENS[2].lstrip("API_SECRET").strip()[1:]
RANDOM_API_KEY = TOKENS[4].lstrip("RANDOM_API_KEY").strip()[1:]


class CHANNEL_TRACKER:
    def __init__(self):
        self.channels, self.types = self.__start__()

    def update(self):
        """Updates the current list of tracked channels."""
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM Tracked")
            data = c.fetchall()
            channels = []
            types = []
            for ch in data:
                channels.append(ch[0])
                types.append(ch[2])
            self.channels = channels
            self.types = types

    def __start__(self):
        # DO NOT CALL MORE THAN ONCE
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM Tracked")
            data = c.fetchall()
            channels = []
            types = []
            for ch in data:
                channels.append(ch[0])
                types.append(ch[2])
            return channels, types


USAGE_QUERY = {
    "jsonrpc": "2.0",
    "method": "getUsage",
    "params": {"apiKey": RANDOM_API_KEY},
    "id": 42,
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
        response = post(
            R_API,
            headers={"User-Agent": "Appelsiini1's Discord Bot"},
            json=USAGE_QUERY,
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
            result = json_response["result"]
            bitsLeft = result["bitsLeft"]
            requestsLeft = result["requestsLeft"]
            self.bitsLeft = bitsLeft
            self.requestsLeft = requestsLeft

    def checkDelay(self):
        now = datetime.today()
        difference = now - self.lastRequest
        if difference.seconds < self.advisoryDelay:
            sleep(abs(int(difference.seconds)))

    def checkLimits(self):
        # Raise error if limit is reached
        if self.bitsLeft <= 15 or self.requestsLeft == 0:
            raise RequestLimitReached

    def resetLimits(self):
        self.requestsLeft = 1000
        self.bitsLeft = 250000


# Keeps track of channels that need to be tracked
TRACKED_CHANNELS = CHANNEL_TRACKER()

# Random API Request limits
REQUEST_LIMITS = requestLimits()

# Version number
VERSION = "v2.0.1"
