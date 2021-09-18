from discord.ext import tasks
from constants import *
import sqlite3
from pytz import utc
from datetime import datetime, time, timedelta
from discord.ext import commands

TEN_MINUTES = time(0, 10, 0, 0)
ONE_MINUTE = time(0, 1, 0, 0)


class EVENT_CHECKER(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def addEvent(ctx, eventType, eventTime, eventName, eventInfo):
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        year = eventTime.strftime("%Y")
        month = eventTime.strftime("%m")
        day = eventTime.strftime("%d")
        hour = eventTime.strftime("%H")
        minute = eventTime.strftime("%M")
        second = eventTime.strftime("%S")

        c.execute(
            "INSERT INTO Scheduler (?,?,?,?,?,?,?,?,?,?,?)",
            (
                None,
                eventType,
                eventName,
                eventTime,
                eventInfo,
                year,
                month,
                day,
                hour,
                minute,
                second,
            ),
        )

        conn.commit()


def delEvent(eventID):
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        c.execute(f"DELETE FROM Scheduler WHERE Event_ID={eventID}")
        conn.commit()


class SCHEDULER(commands.Cog):
    def __init__(self, bot):
        # self.event_checker.start()
        # self.test_loop.start()
        self.bot = bot
        self.LessThanHourTasks = []
        self.LessThanTenTasks = []
        self.LessThanOneTasks = []

    @tasks.loop(minutes=10)
    async def less_than_hour(
        self,
    ):
        current_time = datetime.today()
        for i, event in enumerate(self.LessThanHourTasks):
            event_time = datetime.strptime(event[4])
            if current_time-event_time <= timedelta(seconds=600):
                self.LessThanTenTasks.append(event)
                del self.LessThanHourTasks[i]
                try:
                    self.less_than_ten.start()
                except RuntimeError:
                    pass

    @tasks.loop(minutes=1)
    async def less_than_ten(
        self,
    ):
        current_time = datetime.today()
        for i, event in enumerate(self.LessThanTenTasks):
            event_time = datetime.strptime(event[4])
            if current_time-event_time <= timedelta(seconds=600):
                self.LessThanOneTasks.append(event)
                del self.LessThanTenTasks[i]

    @tasks.loop(seconds=2)
    async def less_than_one(
        self,
    ):
        current_time = datetime.today()
        for i, event in enumerate(self.LessThanOneTasks):
            event_time = datetime.strptime(event[4])
            if current_time-event_time <= timedelta(seconds=2):
                #EVENT STARTUP LOGIC
                
                del self.LessThanOneTasks[i]

    @tasks.loop(seconds=5.0, count=3)
    async def test_loop(
        self,
    ):
        print("test")

    @tasks.loop(hours=1.0)
    async def event_checker(self):
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            current_time = datetime.today()
            year_now = current_time.strftime("%Y")
            month_now = current_time.strftime("%m")
            day_now = current_time.strftime("%d")
            
            c.execute(
                "SELECT * FROM Scheduler WHERE Year=? AND Month=? AND Day=?",
                (year_now, month_now, day_now),
            )
            data = c.fetchall()

            for event in data:
                # Event_ID INTEGER 0
                # Event_type TEXT, 1
                # Event_name TEXT, 2
                # Event_info TEXT, 3
                # Datetime TEXT,   4
                # Year INT,        5
                # Month INT,       6
                # Day INT,         7
                # Hour INT,        8
                # Minute INT,      9
                # Second INT       10
                event_time = datetime.strptime(event[4])

                # check for past/missed events?
                # Add logic to not get events twice
                if current_time-event_time <= timedelta(seconds=3600):
                    self.LessThanHourTasks.append(event)
                    try:
                        self.less_than_hour.start()
                    except RuntimeError:
                        pass


def setup(client):
    client.add_cog(SCHEDULER(client))
    client.add_cog(EVENT_CHECKER(client))
