from discord.ext import tasks
from constants import *
import sqlite3
from pytz import utc
from datetime import datetime, time, timedelta

TEN_MINUTES = time(0, 10, 0, 0)
ONE_MINUTE = time(0, 1, 0, 0)

class EVENT_CHECKER(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @tasks.loop(minutes=1)
    async def less_than_ten():
        pass

    @tasks.loop(seconds=10)
    async def less_than_one():
        pass

# Scheduler event listener
def on_scheduler_event(event):
    if event.exception:
        logging.error(f"Scheduler job failed: {event}")
    else:
        logging.info("Job executed succesfully.")

class SCHEDULER(commands.Cog):
    def __init__(self, bot) -> None:
        #self.event_checker.start()
        #self.test_loop.start()
        self.bot = bot

    @tasks.loop(seconds=5.0, count=3)
    async def test_loop():
        print("test")

    @tasks.loop(minutes=10.0)
    async def event_checker():
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            current_time = datetime.today()
            year_now = current_time.strftime("%Y")
            month_now = current_time.strftime("%m")
            day_now = current_time.strftime("%d")
            c.execute("SELECT * FROM Scheduler WHERE Year=? AND Month=? AND Day=?", (year_now, month_now, day_now))
            data = c.fetchall()

def setup(client):
    client.add_cog(SCHEDULER(client))
    client.add_cog(EVENT_CHECKER(client))