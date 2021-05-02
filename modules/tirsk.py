import sqlite3
import discord
import logging
import time
from modules.common import get_hex_colour
from constants import DB_F, TRACKED_CHANNELS
import datetime
import re
import os

MENTION_RE = re.compile(r"^.*<@!(\d+)>")


async def tirskCount(message):
    logging.info("Started quote counting in {}".format(message.channel.name))
    emb = discord.Embed(
        description="_Counting quotes... (this could take a while)_",
        color=get_hex_colour(),
    )
    msgID = await message.channel.send(embed=emb)
    await message.channel.trigger_typing()
    counter = {}
    async for msg in message.channel.history(limit=None):
        time.sleep(0.08)
        mentions = msg.mentions
        if len(mentions) == 0:
            continue
        elif len(mentions) == 1:
            auth = mentions[0].id
            if auth in counter:
                counter[auth] += 1
            else:
                counter[auth] = 1
        elif len(mentions) >= 2:
            # pos = msg.content.rfind("<")
            # user_id = msg.content[pos:].strip()[3:][:-1]
            match = MENTION_RE.match(msg.content)
            if match:
                user_id = match.group(1)
                user = await message.guild.fetch_member(int(user_id))
                auth = user.id
                if auth in counter:
                    counter[auth] += 1
                else:
                    counter[auth] = 1

    txt = ""
    c_time = datetime.today().strftime("%d.%m.%Y")
    for keypair in sorted(counter.items(), key=lambda x: x[1], reverse=True):
        name = await message.guild.fetch_member(keypair[0])
        time.sleep(0.07)
        if name:
            name = name.display_name
        else:
            name = keypair[0]
        txt += f"{name}: {keypair[1]}\n"
    emb.title = f"Quote Scoreboard {c_time}:"
    emb.description = txt
    await msgID.edit(embed=emb)
    logging.info("Quote counting in {} finished.".format(message.channel.name))


async def tirskTrack(message):
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        mentions = message.mentions
        if len(mentions) == 0:
            await message.add_reaction("\N{no entry}")
        elif len(mentions) == 1:
            auth = mentions[0].id
            # Quote_ID INT UNIQUE,
            # User_ID INT,
            # Channel_ID INT,
            # Guild_ID INT,
            # Quote_text TEXT,
            c.execute("SELECT * FROM Quotes")
            old = c.fetchone()
            Quote_ID = old[0] + 1 if old != None else 1
            success = 0
            for i in range(10):
                try:
                    c.execute(
                        "INSERT INTO Quotes VALUES (?,?,?,?,?)",
                        (
                            Quote_ID,
                            auth,
                            message.channel.id,
                            message.guild.id,
                            message.content,
                        ),
                    )
                    success = 1
                    break
                except sqlite3.IntegrityError:
                    Quote_ID += 1
                    logging.warning(
                        f"Insertion to database failed, new quote ID is {Quote_ID}"
                    )

            if success == 0:
                logging.error("Could not add quote to database due to database error.")
                await message.add_reaction("\N{no entry}")
            else:
                await message.add_reaction("\N{white heavy check mark}")
        elif len(mentions) >= 2:
            # pos = msg.content.rfind("<")
            # user_id = msg.content[pos:].strip()[3:][:-1]
            match = MENTION_RE.match(message.content)
            if match:
                user_id = match.group(1)
                user = await message.guild.fetch_member(int(user_id))
                auth = user.id
                c.execute("SELECT * FROM Quotes")
                old = c.fetchone()
                Quote_ID = old[0] + 1 if old != None else 1
                success = 0
                for i in range(10):
                    try:
                        c.execute(
                            "INSERT INTO Quotes VALUES (?,?,?,?,?)",
                            (
                                Quote_ID,
                                auth,
                                message.channel.id,
                                message.guild.id,
                                message.content,
                            ),
                        )
                        success = 1
                        break
                    except sqlite3.IntegrityError:
                        Quote_ID += 1
                        logging.warning(
                            f"Insertion to database failed, new quote ID is {Quote_ID}"
                        )

                if success == 0:
                    logging.error(
                        "Could not add quote to database due to database error."
                    )
                    await message.add_reaction("\N{no entry}")
                else:
                    await message.add_reaction("\N{white heavy check mark}")
            else:
                await message.add_reaction("\N{no entry}")
                logging.error("Could not make an RE match when parsing quote.")
                logging.info(f"Message content: '{message.content}'")


async def setTracking(message):
    # Command structure
    # !c tirsk [start | stop]

    arg = message.content.split(" ")[2].strip().lstrip("[").rstrip("]").lower()
    if arg == "start":
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM Tracked WHERE Channel_ID=? AND Guild_ID=?",
                (message.channel.id, message.guild.id),
            )
            tr = c.fetchone()
            if tr == None:
                c.execute(
                    "INSERT INTO Tracked VALUES (?,?,?)",
                    (message.channel.id, message.guild.id, 1),
                )
                conn.commit()
                TRACKED_CHANNELS.update()
                emb = discord.Embed()
                emb.description = "Quote tracking started."
                emb.color = get_hex_colour(cora_eye=True)
                await message.channel.send(embed=emb)
            else:
                emb = discord.Embed()
                emb.description = "This channel is already being tracked."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)

    elif arg == "stop":
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM Tracked WHERE Channel_ID=? AND Guil_ID=?",
                (message.channel.id, message.guild.id),
            )
            tr = c.fetchone()
            if tr == None:
                emb = discord.Embed()
                emb.description = "This channel was not tracked."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
            else:
                c.execute(
                    "DELETE FROM Tracked WHERE Channel_ID=? AND Guild_ID=?",
                    (message.channel.id, message.guild.id),
                )
                conn.commit()
                TRACKED_CHANNELS.update()
                emb = discord.Embed()
                emb.description = "Quote tracking stopped."
                emb.color = get_hex_colour(cora_eye=True)
                await message.channel.send(embed=emb)


async def tirskExport(message):
    guildID = message.guild.id
    channelID = message.channel.id

    time = datetime.datetime.now().strftime("%d.%m.%Y at %H:%M")
    emb = discord.Embed()
    emb.description = "_Compiling data, this could take a while._"
    emb.color = get_hex_colour(cora_blonde=True)
    msg = await message.channel.send(embed=emb)
    await message.channel.trigger_typing()

    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT * FROM Quotes WHERE Channel_ID=? AND Guild_ID=?",
            (channelID, guildID),
        )
        quotes = c.fetchall()

        if len(quotes) == 0:
            emb.description = ""
            emb.title = "No quotes to export."
            emb.color = get_hex_colour(error=True)
            await msg.edit(embed=emb)
        else:
            filename = f"export_{channelID}.csv"
            with open(filename, "w", encoding="utf-8") as f:
                f.write("DisplayName;Quote")
                for q in quotes:
                    user = message.guild.get_member(q[1])
                    if user:
                        displayName = user.display_name
                    else:
                        user = await message.guild.fetch_member(q[1])
                        time.sleep(0.07)
                        if user:
                            displayName = user.display_name
                        else:
                            displayName = q[1]
                    f.write(f"{displayName};{q[4]}")

            fileToSend = discord.File(filename)

            emb.description = ""
            emb.title = f"Here is a CSV-file containing all boosts on your server on the bot's database. This export was made on {time}."
            emb.color = get_hex_colour(cora_blonde=True)

            dm_channel = message.author.dm_channel
            if dm_channel == None:
                dm_channel = await message.author.create_dm()
            try:
                await dm_channel.send(file=fileToSend)
                await dm_channel.send(embed=emb)
                emb.title = ""
                emb.description = "**Quote data succesfully compiled and sent to you.**"
                emb.color = get_hex_colour(cora_eye=True)
                await msg.edit(embed=emb)
            except Exception:
                logging.exception(
                    "Unable to send exported quotes to the requester."
                )
                await message.channel.send(
                    "Unable to send exported data due to an error. Please try again."
                )
            try:
                os.remove(filename)
            except Exception as e:
                logging.exception(
                    "Unable to delete the local copy of quote export CSV."
                )


async def tirskJunction(message):
    try:
        arg2 = message.content.split(" ")[2].strip().lstrip("[").rstrip("]").lower()
    except IndexError:
        await message.channel.send(
            "No arguments given. Valid arguments are `count`, `start`, `stop` and `export`."
        )
    if message.author.guild_permissions.administrator:
        if arg2 == "count":
            await tirskCount(message)
        elif arg2 in ["start", "stop"]:
            await setTracking(message)
        elif arg2 == "export":
            await tirskExport(message)
        else:
            await message.channel.send(
                "Unknown argument. Valid arguments are `count`, `start`, `stop` and export."
            )
    else:
        emb = discord.Embed()
        emb.description = "You do not have the permissions to use this."
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)