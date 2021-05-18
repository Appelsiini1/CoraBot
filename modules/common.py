import random
import discord
from modules.emoji_list import _EMOJIS
import sqlite3
import logging
from constants import DB_F


def get_hex_colour(cora_blonde=False, cora_eye=False, error=False):
    """Returns a hex colour as a discord.Colour object
    Args: cora_blonde = [True|False] Default: False
    cora_eye = [True|False] Default: False
    error = [True|False] Default: False"""
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
    txt = ""
    for emoji in _EMOJIS:
        txt += emoji + " ; "
    await message.channel.send(txt)


async def forbiddenErrorHandler(message):
    logging.error("Unable to send message due to 403 - Forbidden")
    emb = discord.Embed()
    emb.description = f"Unable to send message to channel '{message.channel.name}' in '{message.guild.name}'. If you are the server owner, please make sure I have the proper rights to post messages to that channel."
    emb.color = get_hex_colour(error=True)
    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()
    await dm_channel.send(embed=emb)


def initializeDatabase():
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        # BasicPolls Table
        c.execute(
            """CREATE TABLE IF NOT EXISTS BasicPolls(
            Poll_ID INT UNIQUE,
            Ch_ID INT,  
            Guild_ID INT,
            Author_ID INT,
            Emojis TEXT,
            PollName TEXT,
            PRIMARY KEY (Poll_ID)
        );"""
        )

        # RolePolls Table
        c.execute(
            """CREATE TABLE IF NOT EXISTS RolePolls(
            Poll_ID INT UNIQUE,
            Ch_ID INT,
            Guild_ID INT,
            Author_ID INT,
            Options TEXT,
            PollName TEXT,
            PRIMARY KEY (Poll_ID)
        );"""
        )

        # MaxVotes
        c.execute(
            """CREATE TABLE IF NOT EXISTS RolesMaxVotes(
            Role_ID INT UNIQUE,
            Role_name TEXT,
            Guild_ID INT,
            MaxVotes INT,
            PRIMARY KEY (Role_ID)
        );"""
        )

        # Votes for RolePolls Table
        c.execute(
            """CREATE TABLE IF NOT EXISTS RolePolls_Votes(
            Vote_ID INT UNIQUE,
            Poll_ID INT,
            Voter_ID INT,
            Votes TXT,
            PRIMARY KEY (Vote_ID)
            FOREIGN KEY (Poll_ID) REFERENCES RolePolls(Poll_ID)
                ON DELETE CASCADE
        );"""
        )

        # Nitro boosts
        c.execute(
            """CREATE TABLE IF NOT EXISTS NitroBoosts(
            Boost_ID INT UNIQUE,
            User_ID INT,
            Guild_ID INT,
            Boost_Time TEXT,
            LatestBoost TEXT,
            Boosts INT,
            PRIMARY KEY (Boost_ID)
        );"""
        )

        # Servers to track Nitro
        c.execute(
            """CREATE TABLE IF NOT EXISTS NitroTrack(
            Guild_ID INT,
            Track_YN INT,
            PRIMARY KEY (Guild_ID)
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
            Quote_ID INT UNIQUE,
            User_ID INT,
            Channel_ID INT,
            Guild_ID INT,
            Quote_text TEXT,
            PRIMARY KEY (Quote_ID)
        );"""
        )

        # Current auctions
        c.execute(
            """CREATE TABLE IF NOT EXISTS Auctions(
            Auction_ID INT UNIQUE,
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
            PRIMARY KEY (Auction_ID)
        );"""
        )

        # Auction bids
        c.execute(
            """CREATE TABLE IF NOT EXISTS Bids(
            Bid_ID INT UNIQUE,
            Auction_ID INT,
            Slot TEXT,
            Value INT,
            PRIMARY KEY (Bid_ID)
            FOREIGN KEY (Auction_ID) REFERENCES Auctions(Auction_ID)
                ON DELETE CASCADE
        );"""
        )

        # other databases here

        conn.commit()
