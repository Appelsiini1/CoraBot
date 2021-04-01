import random
import discord
import sys
import logging
from modules.emoji_list import _EMOJIS
import sqlite3
import os

CURR_DIR = os.path.dirname(os.path.realpath(__file__))

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

def selectReactionEmoji(n, indexes=False):
    selected = []
    r_ns = []
    i = 0
    while(i<n):
        r_n = random.randint(0, len(_EMOJIS)-1)
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

def initializeDatabase():
    db_file = CURR_DIR + "\\databases.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    #BasicPolls Table
    c.execute('''CREATE TABLE IF NOT EXISTS BasicPolls(
        Poll_ID INT UNIQUE,
        Ch_ID INT,  
        Guild_ID INT,
        Author_ID INT,
        Emojis TEXT,
        PollName TEXT,
        PRIMARY KEY (Poll_ID)
    );''')

    #RolePolls Table
    c.execute('''CREATE TABLE IF NOT EXISTS RolePolls(
        Poll_ID INT UNIQUE,
        Ch_ID INT,
        Guild_ID INT,
        Author_ID INT,
        Options TEXT,
        PollName TEXT,
        PRIMARY KEY (Poll_ID)
    );''')

    #MaxVotes
    c.execute('''CREATE TABLE IF NOT EXISTS RolesMaxVotes(
        Role_ID INT UNIQUE,
        Guild_ID INT,
        MaxVotes INT,
        PRIMARY KEY (Role_ID)
    );''')

    #Votes for RolePolls Table
    c.execute('''CREATE TABLE IF NOT EXISTS RolePolls_Votes(
        Vote_ID INT UNIQUE,
        Poll_ID INT,
        Voter_ID INT,
        option1 INT,
        option2 INT,
        option3 INT,
        option4 INT,
        option5 INT,
        option6 INT,
        option7 INT,
        option8 INT,
        option9 INT,
        option10 INT,
        option11 INT,
        option12 INT,
        option13 INT,
        option14 INT,
        option15 INT,
        option16 INT,
        option17 INT,
        option18 INT,
        option19 INT,
        option20 INT,
        PRIMARY KEY (Vote_ID)
        FOREIGN KEY (Poll_ID) REFERENCES RolePolls(Poll_ID)
            ON DELETE CASCADE
    );''')

    #other databases here

    conn.commit()
    conn.close()