import os
from logging import exception
from sys import exit


def get_tokens():
    """Gets environment variables. Returns a list."""
    try:
        with open(".env", "r") as f:
            tokens = f.readlines()
    except Exception:
        exception("Could not acquire environment variables. Stopping.")
        exit(1)
    return tokens

PREFIX = "!c "
AUTHOR = "This bot is maintained by Appelsiini1"
GIT = "Source code for this bot can be found at https://github.com/Appelsiini1/CoraBot"
DB_F = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Databases", "database.db")
TOKENS = get_tokens()
DISCORD_TOKEN = TOKENS[0].lstrip("TOKEN").strip()[1:]
TWIT_API_KEY = TOKENS[1].lstrip("API_KEY").strip()[1:]
TWIT_API_SECRET = TOKENS[2].lstrip("API_SECRET").strip()[1:]
VERSION = "v1.11.8"