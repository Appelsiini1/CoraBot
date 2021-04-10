import discord
import logging
import sqlite3
from modules.common import get_hex_colour
from constants import DB_F

async def trackNitro(message):
    pass

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