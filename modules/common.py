import random
import discord
from modules.emoji_list import _EMOJIS
import sqlite3
import logging
from pytz import all_timezones
from dateutil import tz
from datetime import datetime
from constants import DB_F


def get_hex_colour(cora_blonde=False, cora_eye=False, error=False):
    """Returns a hex colour as a discord.Colour object

    Args:

    cora_blonde = [True|False] (Default: False)

    cora_eye = [True|False] (Default: False)

    error = [True|False] (Default: False)"""
    if cora_blonde == True:
        color = discord.Colour(value=0xFFCC99)
    elif cora_eye == True:
        color = discord.Colour(value=0x338B41)
    elif error == True:
        color = discord.Colour(value=0xFF0000)
    else:
        random_n = random.randint(0, 16777215)
        color = discord.Colour(value=random_n)

    return color


def selectReactionEmoji(n, indexes=False):
    """Helper function to randomly select n emojis from the emoji list. Returns a list containing the emojis.
    If 'indexes' parameter is set to True, will return the indexes of the emojis in the list instead of the actual emojis."""
    selected = []
    r_ns = []
    i = 0
    while i < n:
        r_n = random.randint(0, len(_EMOJIS) - 1)
        if _EMOJIS[r_n] not in selected:
            selected.append(_EMOJIS[r_n])
            r_ns.append(r_n)
            i += 1
        else:
            continue
    if indexes == True:
        return r_ns
    else:
        return selected


async def sendEmoji(message):
    """Helper function to determine what emojis work with Discord"""
    txt = ""
    for emoji in _EMOJIS:
        txt += emoji + " ; "
    await message.channel.send(txt)


async def forbiddenErrorHandler(message):
    """Handles the error when the bot does not have permission to send a message to channel."""

    logging.error("Unable to send message due to 403 - Forbidden")
    emb = discord.Embed()
    emb.description = f"Unable to send message to channel '{message.channel.name}' in '{message.guild.name}'. If you are the server owner, please make sure I have the proper rights to post messages to that channel."
    emb.color = get_hex_colour(error=True)
    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()
    await dm_channel.send(embed=emb)


def timeParser(timeToParse: str):
    """Parses time data. Input is string in the format 'DD.MM.YYYY HH:MM, Area/Location', where timezone is per the IANA tz database.
    Returns a timezone-aware datetime object converted to local time."""
    # DD.MM.YYYY HH:MM, America/Los_Angeles (as 24-hour clock)(Timezone as per the IANA Database: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)
    naive_time = datetime.strptime(timeToParse.split(",")[0], "%d.%m.%Y %H:%M")
    timezone_raw = timeToParse.split(",")[1].strip().lstrip("[").rstrip("]")
    if timezone_raw in all_timezones:
        timezone = tz.gettz(timezone_raw)
        aware_time = naive_time.replace(tzinfo=timezone)
        server_local_time = aware_time.astimezone(tz.gettz())
        
        return server_local_time
    else:
        raise ValueError

def timeConverter(timeToConvert: datetime, timezone=None):
    """Converts to spesific timezone. If timezone argument is not given, local time is used. timeToConvert must be a datetime object with tzinfo. Returns a datetime object with new tzinfo."""
    new_timezone = tz.gettz(timezone)
    new_time = timeToConvert.astimezone(new_timezone)

    return new_time

def check_if_channel(ctx):
    if ctx.channel.type == discord.ChannelType.text or ctx.channel.type == discord.ChannelType.news:
        return True
    else:
        return False

def check_if_bot(ctx):
    return ctx.author.bot != True

def initializeDatabase():
    """Initializes the required database tables if they do not exist yet.
    Does nothing if they already exist in the database.
    Note: table declarations cannot be edited if they have been already run."""

    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        # BasicPolls Table
        c.execute(
            """CREATE TABLE IF NOT EXISTS BasicPolls(
            Poll_ID INTEGER PRIMARY KEY UNIQUE,
            Ch_ID INT,  
            Guild_ID INT,
            Author_ID INT,
            Emojis TEXT,
            PollOptions TEXT,
            PollName TEXT,
            MSG_ID INT
        );"""
        )

        # RolePolls Table
        c.execute(
            """CREATE TABLE IF NOT EXISTS RolePolls(
            Poll_ID INTEGER UNIQUE PRIMARY KEY,
            Ch_ID INT,
            Guild_ID INT,
            Author_ID INT,
            Options TEXT,
            PollName TEXT,
            Timestamp TEXT
        );"""
        )

        # MaxVotes
        c.execute(
            """CREATE TABLE IF NOT EXISTS RolesMaxVotes(
            Role_ID INTEGER UNIQUE PRIMARY KEY,
            Role_name TEXT,
            Guild_ID INT,
            MaxVotes INT
        );"""
        )

        # Votes for RolePolls Table
        c.execute(
            """CREATE TABLE IF NOT EXISTS RolePolls_Votes(
            Vote_ID INTEGER UNIQUE PRIMARY KEY,
            Poll_ID INT,
            Voter_ID INT,
            Votes TXT,
            Timestamp TEXT,
            FOREIGN KEY (Poll_ID) REFERENCES RolePolls(Poll_ID)
                ON DELETE CASCADE
        );"""
        )

        # Nitro boosts
        c.execute(
            """CREATE TABLE IF NOT EXISTS NitroBoosts(
            Boost_ID INTEGER UNIQUE PRIMARY KEY,
            User_ID INT,
            Guild_ID INT,
            Boost_Time TEXT,
            LatestBoost TEXT,
            Boosts INT
        );"""
        )

        # Servers to track Nitro
        c.execute(
            """CREATE TABLE IF NOT EXISTS NitroTrack(
            Guild_ID INTEGER PRIMARY KEY,
            Track_YN INT
        );"""
        )

        # Channels to track (other than Nitro)
        c.execute(
            """CREATE TABLE IF NOT EXISTS Tracked(
            Channel_ID INT,
            Guild_ID INT,
            Type INT,
            PRIMARY KEY (Channel_ID)
        );"""
        )

        # Quote table
        c.execute(
            """CREATE TABLE IF NOT EXISTS Quotes(
            Quote_ID INTEGER UNIQUE PRIMARY KEY,
            User_ID INT,
            Channel_ID INT,
            Guild_ID INT,
            Quote_text TEXT
        );"""
        )

        # ID table
        c.execute(
            """CREATE TABLE IF NOT EXISTS IDs(
            ID INTEGER PRIMARY KEY,
            Type TEXT
        );"""
        )

        # Current auctions
        c.execute(
            """CREATE TABLE IF NOT EXISTS Auctions(
            Auction_ID INTEGER UNIQUE PRIMARY KEY,
            Channel_ID INT,
            Guild_ID INT,
            Author_ID INT,
            Slots TEXT,
            Currency TEXT,
            Starting_bid INT,
            Min_increase INT,
            Autobuy INT,
            Start_time TEXT,
            End_time TEXT,
            Title TEXT
        );"""
        )

        # Auction bids
        c.execute(
            """CREATE TABLE IF NOT EXISTS Bids(
            Bid_ID INTEGER UNIQUE PRIMARY KEY,
            Auction_ID INT,
            Slot TEXT,
            Value INT,
            FOREIGN KEY (Auction_ID) REFERENCES Auctions(Auction_ID)
                ON DELETE CASCADE
        );"""
        )

        # Scheduled events
        c.execute(
            """CREATE TABLE IF NOT EXISTS Scheduler(
            Event_ID INTEGER UNIQUE PRIMARY KEY,
            Event_type TEXT,
            Event_name TEXT,
            Event_info TEXT,
            Datetime TEXT,
            Year INT,
            Month INT,
            Day INT,
            Hour INT,
            Minute INT,
            Second INT,
            Timezone TEXT,
            Repeat INT,
            Repeat_interval TEXT
        );"""
        )

        # other databases here

        conn.commit()
