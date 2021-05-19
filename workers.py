import discord
from constants import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from pytz import utc


# Scheduler event listener
def on_scheduler_event(event):
    if event.exception:
        logging.error(f"Scheduler job failed: {event}")
    else:
        logging.info("Job executed succesfully.")



# Global functions
SCHEDULER = AsyncIOScheduler()
SCHEDULER.configure(
    jobstores=SCHEDULER_CONFIG[0],
    executors=SCHEDULER_CONFIG[1],
    job_defaults=SCHEDULER_CONFIG[2],
)
SCHEDULER.add_listener(on_scheduler_event, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)
SCHEDULER.start()

CLIENT = discord.Client(intents=INTENTS, activity=ACTIVITY)