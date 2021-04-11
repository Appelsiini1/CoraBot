import discord
import logging
import sqlite3
import datetime
from modules.common import get_hex_colour
from constants import DB_F

async def trackNitro(message):
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        guild_id = message.guild.id
        booster_id = message.author.id

        c.execute("SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?", (guild_id, booster_id))
        previousBoosts = c.fetchall()
        if len(previousBoosts) == 0:
            time = datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")
            c.execute("SELECT Boost_ID FROM NitroBoosts ORDER BY Boost_ID DESC")
            lastID = c.fetchone()
            if lastID == None:
                lastID = 1
            
            # Boost_ID INT UNIQUE,
            # User_ID INT,
            # Guild_ID INT,
            # Boost_Time TEXT,
            # Boosts INT,
            c.execute("INSERT INTO NitroBoosts VALUES (?,?,?,?,?)", (lastID, booster_id, guild_id, time, 1))


async def addNitro(message):
    pass

async def parseNitroAddition(message):
    pass

async def delNitro(message):
    pass

async def test(message):
    # !c test []

    id = int(message.content[8:])
    msg = await message.channel.fetch_message(id)
    print(msg.system_content)
    print(msg.raw_mentions)
    print(msg.author)
    print(msg.is_system())
    print(msg.type)