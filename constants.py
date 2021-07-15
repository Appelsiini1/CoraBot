import os
import logging
from sys import exit
import sqlite3
from discord import Intents, Game
from discord.ext import commands


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


# Keeps track of channels that need to be tracked
TRACKED_CHANNELS = CHANNEL_TRACKER()


# Version number
VERSION = "v2.0.0 ALPHA 6"
