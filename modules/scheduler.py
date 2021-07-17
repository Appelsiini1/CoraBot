from discord.ext import tasks
from constants import *
import sqlite3
from pytz import utc


# Scheduler event listener
def on_scheduler_event(event):
    if event.exception:
        logging.error(f"Scheduler job failed: {event}")
    else:
        logging.info("Job executed succesfully.")


def addEvent(eventType):
    pass


def delEvent(eventID):
    pass


class SCHEDULER:
    def __init__(self):
        # self.event_checker.start()
        # self.test_loop.start()
        pass

    @tasks.loop(seconds=5.0, count=3)
    async def test_loop():
        print("test")

    @tasks.loop(minutes=10.0)
    async def event_checker():
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
