import random
import discord
import sys
import logging
from modules.emoji_list import _EMOJIS
import sqlite3
import os

def get_hex_colour(cora_blonde=False, cora_eye=False, error=False):
    """Returns a hex colour as a discord.Colour object
Args: cora_blonde = [True|False] Default: False
cora_eye = [True|False] Default: False
error = [True|False] Default: False"""
    if cora_blonde == True:
        color = discord.Colour(value=0xffcc99)
    elif cora_eye == True:
        color = discord.Colour(value=0x338b41)
    elif error == True:
        color = discord.Colour(value=0xFF0000)
    else:
        random_n = random.randint(0,16777215)
        color = discord.Colour(value=random_n)
    
    return color

def get_tokens():
    """Gets environment variables. Returns a list."""
    try:
        with open(".env", "r") as f:
            tokens = f.readlines()
    except Exception:
        logging.exception("Could not acquire environment variables. Stopping.")
        sys.exit(1)
    return tokens

def selectReactionEmoji(n):
    selected = []
    i = 0
    while(i<n):
        r_n = random.randint(0, len(_EMOJIS))
        if _EMOJIS[r_n] not in selected:
            selected.append(_EMOJIS[r_n])
            i += 1
        else:
            continue
    return selected

async def sendEmoji(message):
    txt = ""
    for emoji in _EMOJIS:
        txt += emoji + " ; "
    await message.channel.send(txt)

def initializeDatabase(dir):
    db_file = dir + "\\databases.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS BasicPolls(
        Poll_ID INT,
        Ch_ID INT,
        Guild_ID INT,
        PRIMARY KEY (Poll_ID)
    );''')
    #other databases here

    conn.commit()
    conn.close()