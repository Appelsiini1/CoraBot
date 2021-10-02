import re
import discord
import logging
import sqlite3
import datetime
import os
from time import sleep

from modules.common import forbiddenErrorHandler, get_hex_colour
from modules.command_help import nitroHelp
from constants import DB_F
from discord.ext import commands
from modules.random_api import randInt

EMOJI = "\N{PARTY POPPER}"
EMOJI2 = "\N{CONFETTI BALL}"
HEART_EMOTE = "\N{SPARKLING HEART}"
SURPRISE_EMOTE = "\N{FACE WITH OPEN MOUTH}"

MENTION_RE = re.compile(r"^.*<@!(\d+)>")

SPIN_GIF_URL = "https://imgur.com/maohyNQ"


def constructEmbed(message, boosts):
    emb = discord.Embed()

    if message.guild.id == 181079344611852288:  # TinyCactus easter egg
        emote_name = "cheart"
        emote_name2 = "cacsurp2"
        succ = 0
        try:
            for em in message.guild.emojis:
                if em.name == emote_name:
                    H_e = em
                    succ += 1
                if em.name == emote_name2:
                    C_s = em
                if succ == 2:
                    break
            HeartEmote = str(H_e)
            SurpriseEmote = str(C_s)
        except Exception:
            logging.exception(
                "Error occured when getting 'cheart' or 'cacsurp2' emote. Using defaults."
            )
            HeartEmote = HEART_EMOTE
            SurpriseEmote = SURPRISE_EMOTE
    else:
        HeartEmote = HEART_EMOTE
        SurpriseEmote = SURPRISE_EMOTE

    if boosts == 1:
        txt = f"{HeartEmote}  {message.guild.name} just got a New Boost by **{message.author.display_name}**!  {HeartEmote}"
    else:
        txt = f"{HeartEmote}  {message.guild.name} just got {boosts} ({SurpriseEmote}) New Boosts by **{message.author.display_name}**!  {HeartEmote}"

    emb.title = f"{EMOJI} {EMOJI} NEW BOOST! {EMOJI} {EMOJI}"
    emb.color = get_hex_colour(cora_eye=True)
    if message.type == discord.MessageType.premium_guild_subscription:
        emb.description = f"{txt}"
    elif message.type == discord.MessageType.premium_guild_tier_1:
        emb.description = f"{txt}\n\
            {EMOJI2}  {EMOJI}  The server has leveled up to Level 1!  {EMOJI}  {EMOJI2}"
    elif message.type == discord.MessageType.premium_guild_tier_2:
        emb.description = f"{txt}\n\
            {EMOJI2}  {EMOJI}  The server has leveled up to Level 2!  {EMOJI}  {EMOJI2}"
    elif message.type == discord.MessageType.premium_guild_tier_3:
        emb.description = f"{txt}\n\
            {EMOJI2}  {EMOJI}  The server has leveled up to Level 3!  {EMOJI}  {EMOJI2}"
    return emb


# From on_message
async def trackNitro(message):
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        guild_id = message.guild.id
        booster_id = message.author.id
        time = datetime.datetime.now().strftime("%d.%m.%Y")
        emb = discord.Embed()

        try:
            boostAmount = int(message.content)
        except Exception:
            boostAmount = 1

        c.execute(f"SELECT * FROM NitroTrack WHERE Guild_ID={guild_id}")
        track = c.fetchone()
        if track == None:
            return
        elif track[1] == 2:  # Only notice, no tracking.
            emb = constructEmbed(message, boostAmount)
            try:
                await message.channel.send(embed=emb)
                return
            except discord.errors.Forbidden:
                logging.error("Unable to send message due to 403 - Forbidden")
                emb.clear_fields()
                emb.description = f"Unable to send boost announcement to system message channel in '{message.guild.name}'. Please make sure I have the proper rights to post messages to that channel."
                emb.color = get_hex_colour(error=True)
                dm_channel = message.guild.owner.dm_channel
                if dm_channel == None:
                    dm_channel = await message.guild.owner.create_dm()
                await dm_channel.send(embed=emb)
                return

        c.execute(
            "SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
            (guild_id, booster_id),
        )
        previousBoosts = c.fetchone()
        # print(previousBoosts)
        if previousBoosts == None:
            # Boost_ID INT UNIQUE,
            # User_ID INT,
            # Guild_ID INT,
            # Boost_Time TEXT,
            # LatestBoost TEXT,
            # Boosts INT,
            c.execute(
                "INSERT INTO NitroBoosts VALUES (?,?,?,?,?,?)",
                (None, booster_id, guild_id, time, time, boostAmount),
            )

            emb = constructEmbed(message, boostAmount)
            try:
                conn.commit()
                await message.channel.send(embed=emb)
            except discord.errors.Forbidden:
                logging.error("Unable to send message due to 403 - Forbidden")
                emb.clear_fields()
                emb.description = f"Unable to send boost announcement to system message channel in '{message.guild.name}'. Please make sure I have the proper rights to post messages to that channel."
                emb.color = get_hex_colour(error=True)
                dm_channel = message.guild.owner.dm_channel
                if dm_channel == None:
                    dm_channel = await message.guild.owner.create_dm()
                await dm_channel.send(embed=emb)
                return

        else:
            c.execute(
                "SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
                (guild_id, booster_id),
            )
            boost = c.fetchone()
            boosts = boost[5]
            newValue = boosts + boostAmount
            try:

                c.execute(
                    "UPDATE NitroBoosts SET Boosts=?, LatestBoost=? WHERE Guild_ID=? AND User_ID=?",
                    (newValue, time, guild_id, booster_id),
                )
            except Exception:
                logging.exception("Error updating existing boost in database.")
                logging.error(
                    f"newValue: {newValue}, time {time}, guild {message.guild.name}, booster {message.author.name}"
                )
                emb.clear_fields()
                emb.description = f"Unable to update boost entry for {message.author.name} in '{message.guild.name}'. Please contact the developer."
                emb.color = get_hex_colour(error=True)
                dm_channel = message.guild.owner.dm_channel
                if dm_channel == None:
                    dm_channel = await message.guild.owner.create_dm()
                await dm_channel.send(embed=emb)
                return

            emb = constructEmbed(message, boostAmount)
            try:
                conn.commit()
                await message.channel.send(embed=emb)
            except discord.errors.Forbidden:
                logging.error("Unable to send message due to 403 - Forbidden")
                emb.clear_fields()
                emb.description = f"Unable to send boost announcement to system message channel in '{message.guild.name}'. Please make sure I have the proper rights to post messages to that channel.\n\
                The boost was succesfully recorded to database though."
                emb.color = get_hex_colour(error=True)
                dm_channel = message.guild.owner.dm_channel
                if dm_channel == None:
                    dm_channel = await message.guild.owner.create_dm()
                await dm_channel.send(embed=emb)
                return
            except Exception:
                logging.exception("Something went wrong committing database changes.")
                emb.clear_fields()
                emb.description = f"Something went wrong when trying to add latest boost in {message.guild.name} to the database. Please add it manually."
                emb.color = get_hex_colour(error=True)
                dm_channel = message.guild.owner.dm_channel
                if dm_channel == None:
                    dm_channel = await message.guild.owner.create_dm()
                await dm_channel.send(embed=emb)
                return


class Nitro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # tracking control
    async def Tracking(self, message):
        # Command
        # "!c nitro track [start|stop|notice]"
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            arg = message.content.split(" ")[2].strip().lstrip("[").rstrip("]").lower()
            emb = discord.Embed()
            # print(arg)
            if arg == "start":
                c.execute(f"SELECT * FROM NitroTrack WHERE Guild_ID={message.guild.id}")
                trackStatus = c.fetchone()
                if trackStatus == None:
                    c.execute(
                        "INSERT INTO NitroTrack VALUES (?,?)", (message.guild.id, 1)
                    )
                    conn.commit()
                    emb.title = "Nitro boost tracking has been enabled for this server."
                    emb.color = get_hex_colour(cora_eye=True)
                    await message.channel.send(embed=emb)
                    return

                elif trackStatus[1] == 1:
                    emb.title = (
                        "The nitro boost tracking is already enabled on this server."
                    )
                    emb.color = get_hex_colour(error=True)
                    await message.channel.send(embed=emb)
                    return

                elif trackStatus[1] == 2 or trackStatus[1] == 0:
                    c.execute(
                        f"UPDATE NitroTrack SET Track_YN=1 WHERE Guild_ID={message.guild.id}"
                    )
                    conn.commit()
                    emb.title = "Nitro boost tracking has been enabled for this server."
                    emb.color = get_hex_colour(cora_eye=True)
                    await message.channel.send(embed=emb)
                    return

            elif arg == "stop":
                c.execute(f"SELECT * FROM NitroTrack WHERE Guild_ID={message.guild.id}")
                trackStatus = c.fetchone()
                if trackStatus == None:
                    c.execute(
                        "INSERT INTO NitroTrack VALUES (?,?)", (message.guild.id, 0)
                    )
                    conn.commit()
                    emb.title = (
                        "Nitro boost tracking has been disabled for this server."
                    )
                    emb.color = get_hex_colour(cora_eye=True)
                    await message.channel.send(embed=emb)
                    return

                elif trackStatus[1] == 0:
                    emb.title = (
                        "Nitro boost tracking is already disabled on this server."
                    )
                    emb.color = get_hex_colour(error=True)
                    await message.channel.send(embed=emb)
                    return

                elif trackStatus[1] == 2 or trackStatus[1] == 1:
                    c.execute(
                        f"UPDATE NitroTrack SET Track_YN=0 WHERE Guild_ID={message.guild.id}"
                    )
                    conn.commit()
                    emb.title = (
                        "Nitro boost tracking has been disabled for this server."
                    )
                    emb.color = get_hex_colour(cora_eye=True)
                    await message.channel.send(embed=emb)
                    return

            elif arg == "notice":
                c.execute(f"SELECT * FROM NitroTrack WHERE Guild_ID={message.guild.id}")
                trackStatus = c.fetchone()
                if trackStatus == None:
                    c.execute(
                        "INSERT INTO NitroTrack VALUES (?,?)", (message.guild.id, 2)
                    )
                    conn.commit()
                    emb.title = (
                        "Nitro boosts will now only be announced on this server."
                    )
                    emb.color = get_hex_colour(cora_eye=True)
                    await message.channel.send(embed=emb)
                    return

                elif trackStatus[1] == 2:
                    emb.title = (
                        "The nitro boost tracking is already disabled on this server."
                    )
                    emb.color = get_hex_colour(error=True)
                    await message.channel.send(embed=emb)
                    return

                elif trackStatus[1] == 0 or trackStatus[1] == 1:
                    c.execute(
                        f"UPDATE NitroTrack SET Track_YN=2 WHERE Guild_ID={message.guild.id}"
                    )
                    conn.commit()
                    emb.title = (
                        "Nitro boosts will now only be announced on this server."
                    )
                    emb.color = get_hex_colour(cora_eye=True)
                    await message.channel.send(embed=emb)
                    return

    # manual add
    async def addNitro(self, message):
        # command structure
        # !c nitro add [@user or id], [amount], [time ONLY DATE!! as DD.MM.YYYY]
        # if time is omitted, use current time
        prefix = "!c nitro add "
        args = message.content[len(prefix) :].split(",")

        emb = discord.Embed()

        try:
            user_raw = args[0].strip().lstrip("[").rstrip("]")
            boostAmount = int(args[1].strip().lstrip("[").rstrip("]"))
        except Exception:
            emb.title = "Invalid user ID or boost amount. Give user as an ID or a mention. Boost amount should be an integer. Also make sure you have commas in the right place."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            return

        match = MENTION_RE.match(user_raw)
        if match:
            user_id = match.group(1)
            user = await message.guild.fetch_member(int(user_id))
        else:
            try:
                user_id = int(user_raw)
                user = await message.guild.fetch_member(user_id)
            except Exception:
                emb.title = "Invalid user ID, boost amount or user not found. Give user as an ID or a mention. Boost amount should be an integer."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return
        noTime = 0
        try:
            time = args[2].strip().lstrip("[").rstrip("]").strip("'")
        except Exception:
            boostTime = datetime.datetime.today()
            noTime = 1
        if noTime == 0:
            try:
                boostTime = datetime.datetime.strptime(time, "%d.%m.%Y")
            except ValueError:
                emb.title = "Invalid timeformat. Please give boost time in the format `DD.MM.YYYY`."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

        guild_id = message.guild.id
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
                (guild_id, user.id),
            )
            previousBoosts = c.fetchone()
            if previousBoosts == None:
                # Boost_ID INT UNIQUE, 0
                # User_ID INT, 1
                # Guild_ID INT, 2
                # Boost_Time TEXT, 3
                # LatestBoost TEXT, 4
                # Boosts INT, 5

                c.execute(
                    "INSERT INTO NitroBoosts VALUES (?,?,?,?,?,?)",
                    (
                        None,
                        user.id,
                        guild_id,
                        boostTime.strftime("%d.%m.%Y"),
                        boostTime.strftime("%d.%m.%Y"),
                        boostAmount,
                    ),
                )

                emb.description = f"Added {boostAmount} boost(s) by {user.display_name} into database."
                emb.color = get_hex_colour(cora_eye=True)
                conn.commit()
                await message.channel.send(embed=emb)

            else:
                c.execute(
                    "SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
                    (guild_id, user.id),
                )
                boost = c.fetchone()
                boosts = boost[5]
                oldBoostTime = datetime.datetime.strptime(boost[4], "%d.%m.%Y")
                newValue = boosts + boostAmount
                if boostTime < oldBoostTime:
                    if boostTime < oldBoostTime:
                        c.execute(
                            "UPDATE NitroBoosts SET Boosts=?, Boost_Time=? WHERE Guild_ID=? AND User_ID=?",
                            (
                                newValue,
                                boostTime.strftime("%d.%m.%Y"),
                                guild_id,
                                user.id,
                            ),
                        )
                else:
                    c.execute(
                        "UPDATE NitroBoosts SET Boosts=?, LatestBoost=? WHERE Guild_ID=? AND User_ID=?",
                        (newValue, boostTime.strftime("%d.%m.%Y"), guild_id, user.id),
                    )
                emb.description = f"Added {boostAmount} boost(s) by {user.display_name} into database."
                emb.color = get_hex_colour(cora_eye=True)
                conn.commit()
                await message.channel.send(embed=emb)

    # manual delete
    async def delNitro(self, message):
        # Command structure
        # !c nitro del @person (amount / 'all')

        prefix = "!c nitro del "
        args = message.content[len(prefix) :].split(",")

        emb = discord.Embed()

        try:
            user_raw = args[0].strip().lstrip("[").rstrip("]")
            boostAmount = int(args[1].strip().lstrip("[").rstrip("]"))
        except IndexError:
            emb.title = "Invalid user ID or boost amount. Give user as an ID or a mention. Boost amount should be an integer."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            return
        except ValueError:
            if args[1].strip().lstrip("[").rstrip("]").lower() == "all":
                boostAmount = 99999
            else:
                emb.title = "Invalid user ID or boost amount. Give user as an ID or a mention. Boost amount should be an integer."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

        match = MENTION_RE.match(user_raw)
        if match:
            user_id = match.group(1)
            user = await message.guild.fetch_member(int(user_id))
        else:
            try:
                user_id = int(user_raw)
                user = await message.guild.fetch_member(user_id)
            except Exception:
                emb.title = "Invalid user ID or user not found. Give user as an ID or a mention. Boost amount should be an integer."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

        guild_id = message.guild.id
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
                (guild_id, user.id),
            )
            previousBoosts = c.fetchone()
            if previousBoosts == None:
                emb.title = "User has no boosts on record to delete."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return
            else:
                c.execute(
                    "SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
                    (guild_id, user.id),
                )
                boost = c.fetchone()
                boosts = boost[5]
                newValue = boosts - boostAmount
                try:
                    if boostAmount == 99999 or newValue <= 0:
                        c.execute(
                            "DELETE FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
                            (guild_id, user.id),
                        )
                        emb.description = f"Deleted all ({boosts}) boosts by {user.display_name} from the database."

                    else:
                        c.execute(
                            "UPDATE NitroBoosts SET Boosts=? WHERE Guild_ID=? AND User_ID=?",
                            (newValue, guild_id, user.id),
                        )
                        emb.description = f"Deleted {boostAmount} boost(s) by {user.display_name} from the database."

                except Exception:
                    logging.exception("Error updating database in 'nitro del' command.")
                    emb.title = (
                        "Something went wrong updating database. Please try again."
                    )
                    emb.color = get_hex_colour(error=True)
                    await message.channel.send(embed=emb)
                    return

                emb.color = get_hex_colour(cora_eye=True)
                conn.commit()
                await message.channel.send(embed=emb)

    # boost listing
    async def listNitro(self, message):
        guildID = message.guild.id
        time = datetime.datetime.now().strftime("%d.%m.%Y at %H:%M")
        emb = discord.Embed()
        emb.description = "_Compiling data, this could take a while._"
        emb.color = get_hex_colour(cora_blonde=True)
        msg = await message.channel.send(embed=emb)
        await message.channel.trigger_typing()

        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT * FROM NitroBoosts WHERE Guild_ID={guildID}",
            )
            boosts = c.fetchall()
            if len(boosts) == 0:
                emb.description = ""
                emb.title = "No boosts on record to export."
                emb.color = get_hex_colour(error=True)
                await msg.edit(embed=emb)
            else:
                # Boost_ID INT UNIQUE, 0
                # User_ID INT, 1
                # Guild_ID INT, 2
                # Boost_Time TEXT, 3
                # LatestBoost TEXT, 4
                # Boosts INT 5
                btext = "**Name, Boost Amount**\n"
                texts = []

                for i, b in enumerate(boosts, start=1):
                    user = message.guild.get_member(b[1])
                    if user == None:
                        message.guild.fetch_member(b[1])
                        if user == None:
                            user = b[1]
                        else:
                            user = user.name
                    else:
                        user = user.name
                    btext += f"**{user}** \N{sparkles} {b[5]}\n"
                    if len(btext) >= 4048:
                        texts.append(btext)
                        btext = ""
                
                texts.append(btext)
                texts_len = len(texts)
                
                title = f"Nitro boosters in {message.guild.name}"
                emb2 = discord.Embed()
                emb2.color = get_hex_colour(cora_blonde=True)

                for i, t in enumerate(texts, start=1):
                    if i == 1:
                        emb2.title = title
                        emb2.description = t
                        try:
                            await msg.edit(embed=emb2)
                        except discord.Forbidden:
                            forbiddenErrorHandler(message)
                            return
                        continue
                    elif i == 2:
                        emb2.title = ""
                    emb2.description = t
                    if i == texts_len:
                        emb2.set_footer(text=f"Data fetched: {time}")
                    try:
                        await message.channel.send(embed=emb2)
                    except discord.Forbidden:
                        forbiddenErrorHandler(message)
                        return

    # boost export
    async def exportNitro(self, message):
        guildID = message.guild.id
        time = datetime.datetime.now().strftime("%d.%m.%Y at %H:%M")
        emb = discord.Embed()
        emb.description = "_Compiling data, this could take a while._"
        emb.color = get_hex_colour(cora_blonde=True)
        msg = await message.channel.send(embed=emb)
        await message.channel.trigger_typing()

        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute(
                f"SELECT * FROM NitroBoosts WHERE Guild_ID={guildID}",
            )
            boosts = c.fetchall()

            if len(boosts) == 0:
                emb.description = ""
                emb.title = "No boosts on record to export."
                emb.color = get_hex_colour(error=True)
                await msg.edit(embed=emb)
            else:
                filename = f"export_{guildID}.csv"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write("DisplayName;EarliestBoost;LatestBoost;NumberOfBoosts\n")
                    for b in boosts:
                        # Boost_ID INT UNIQUE,
                        # User_ID INT,
                        # Guild_ID INT,
                        # Boost_Time TEXT,
                        # LatestBoost TEXT,
                        # Boosts INT,
                        user = message.guild.get_member(b[1])
                        if user:
                            user = user.display_name
                        else:
                            user = await message.guild.fetch_member(b[1])
                            sleep(0.08)
                            if user:
                                user = user.display_name
                            else:
                                user = b[1]
                        f.write(f"{user};{b[3]};{b[4]};{b[5]}\n")

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
                    emb.description = (
                        "**Boost data succesfully compiled and sent to you.**"
                    )
                    emb.color = get_hex_colour(cora_eye=True)
                    await msg.edit(embed=emb)
                except Exception:
                    logging.exception(
                        "Unable to send exported nitro boosts to server owner."
                    )
                    await message.channel.send(
                        "Unable to send exported data due to an error. Please try again."
                    )
                try:
                    os.remove(filename)
                except Exception as e:
                    logging.exception(
                        "Unable to delete the local copy of boost export CSV."
                    )

    # validity checks
    async def checkNitro(self, message, checkType="normal"):
        guild_id = message.guild.id
        current_nitros = message.guild.premium_subscribers
        emb = discord.Embed()
        if checkType == "normal":
            emb.description = "_Checking the status of nitro subscribers_"
            emb.color = get_hex_colour(cora_blonde=True)
            msg = await message.channel.send(embed=emb)
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            if len(current_nitros) == 0:
                c.execute(f"DELETE FROM NitroBoosts WHERE Guild_ID={guild_id}")
                if checkType == "normal":
                    emb.description = "No boosts were active so all boosts where deleted from the database."
                    emb.color = get_hex_colour(error=True)
                    conn.commit()
                    await msg.edit(embed=emb)
                    return
                else:
                    conn.commit()
                    return []
            c.execute(f"SELECT * FROM NitroBoosts WHERE Guild_ID={guild_id}")
            db_subscribers = c.fetchall()
            if len(db_subscribers) == 0:
                if checkType == "normal":
                    emb.description = "No boosts currently in database."
                    emb.color = get_hex_colour(error=True)
                    await msg.edit(embed=emb)
                elif checkType == "spin":
                    return []
            else:
                if len(db_subscribers) == len(current_nitros):
                    if checkType == "normal":
                        emb.description = "All nitro boosters still have valid boosts."
                        await msg.edit(embed=emb)
                        return
                    else:
                        return db_subscribers
                results = []
                notFound = []
                for db_s in db_subscribers:
                    found = 0
                    for c_s in current_nitros:
                        if c_s.id == db_s[1]:
                            results.append(db_s)
                            found = 1
                    if found == 0:
                        notFound.append(db_s)

                amountDeleted = len(notFound)
                for db_s in notFound:
                    c.execute(
                        "DELETE FROM NitroBoosts WHERE Guild_ID=? AND Boost_ID=?",
                        (guild_id, db_s[0]),
                    )
                if checkType == "normal":
                    emb.description = f"{amountDeleted} users with expired boosts were deleted from the database."
                    conn.commit()
                    await message.channel.send(embed=emb)
                else:
                    conn.commit()
                    return results

    # spin
    async def nitroSpin(self, message):
        # Command structure
        # !c nitro spin [-e]

        nitroBoosts = await self.checkNitro(message, checkType="spin")

        # For debug purposes
        # with sqlite3.connect(DB_F) as conn:
        #     c = conn.cursor()
        #     c.execute(f"SELECT * FROM NitroBoosts WHERE Guild_ID={message.guild.id}")
        #     nitroBoosts = c.fetchall()

        flag = message.content.split(" ")[-1].strip().lstrip("[").rstrip("]").lower()
        emb = discord.Embed()
        if len(nitroBoosts) == 0:
            emb.description = "No boosts to draw a winner from."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            return

        emb2 = discord.Embed()
        emb2.description = "**_SPIIIIIIIIIIIIIIIIIIIIIIIN!_**"
        emb2.color = get_hex_colour()

        await message.channel.send(embed=emb2)
        await message.channel.send(SPIN_GIF_URL)
        sleep(0.5)
        await message.channel.trigger_typing()
        sleep(9.5)

        if len(nitroBoosts) == 1:
            winner_id = nitroBoosts[0][1]
        else:
            userPool = []
            if flag == "-e":
                for b in nitroBoosts:
                    userPool.append(b[1])
            else:
                for b in nitroBoosts:
                    if b[5] == 1:
                        userPool.append(b[1])
                    else:
                        for i in range(b[5]):
                            userPool.append(b[1])
            winnerIndex = randInt(1, 0, len(userPool) - 1, message.id)[0]
            winner_id = userPool[winnerIndex]

        member = message.guild.get_member(winner_id)
        emb.title = f"_And the winner is..._"
        emb.description = f"{member.mention}!! {EMOJI} {EMOJI}\nCongratulations to the winner! {HEART_EMOTE}"
        emb.color = get_hex_colour()

        await message.channel.send(embed=emb)

    # Junction
    @commands.command(name="nitro")
    async def nitroJunction(self, ctx):
        try:
            arg2 = (
                ctx.message.content.split(" ")[2]
                .strip()
                .lstrip("[")
                .rstrip("]")
                .lower()
            )
        except IndexError:
            await ctx.send(
                "No arguments given. Use `!c nitro help` for correct syntax."
            )
            return
        if ctx.author.guild_permissions.administrator:
            if arg2 in ["start", "stop", "notice"]:
                await self.Tracking(ctx.message)
            elif arg2 == "add":
                await self.addNitro(ctx.message)
            elif arg2 == "del":
                await self.delNitro(ctx.message)
            elif arg2 == "help":
                await nitroHelp(ctx.message)
            elif arg2 == "export":
                if ctx.author.id == ctx.guild.owner_id:
                    await self.exportNitro(ctx.message)
                else:
                    emb = discord.Embed()
                    emb.description = "You do not have the permissions to use this. Only server owners can use this command."
                    emb.color = get_hex_colour(error=True)
                    await ctx.send(embed=emb)
            elif arg2 == "check":
                await self.checkNitro(ctx.message)
            elif arg2 == "spin":
                await self.nitroSpin(ctx.message)
            elif arg2 == "list":
                await self.listNitro(ctx.message)
            else:
                await ctx.send(
                    "Unknown argument. Use `!c nitro help` for correct syntax."
                )
        else:
            if arg2 == "help":
                await nitroHelp(ctx.message)
            else:
                emb = discord.Embed()
                emb.description = "You do not have the permissions to use this."
                emb.color = get_hex_colour(error=True)
                await ctx.send(embed=emb)


def setup(client):
    client.add_cog(Nitro(client))