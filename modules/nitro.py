import re
import discord
import logging
import sqlite3
import datetime

from modules.common import get_hex_colour
from constants import DB_F

EMOJI = "\N{PARTY POPPER}"
EMOJI2 = "\N{CONFETTI BALL}"
HEART_EMOTE = "\N{SPARKLING HEART}"
SURPRISE_EMOTE = "\N{FACE WITH OPEN MOUTH}"

MENTION_RE = re.compile(r"^.*<@!(\d+)>")


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
            c.execute("SELECT Boost_ID FROM NitroBoosts ORDER BY Boost_ID DESC")
            lastID = c.fetchone()
            if lastID == None:
                lastID = 1
            else:
                lastID = lastID[0] + 1

            # Boost_ID INT UNIQUE,
            # User_ID INT,
            # Guild_ID INT,
            # Boost_Time TEXT,
            # LatestBoost TEXT,
            # Boosts INT,
            i = 0
            success = 0
            while i < 10:
                try:
                    c.execute(
                        "INSERT INTO NitroBoosts VALUES (?,?,?,?,?,?)",
                        (lastID, booster_id, guild_id, time, time, boostAmount),
                    )
                    success = 1
                    break
                except sqlite3.IntegrityError:
                    i += 1
                    lastID += 1
            if success != 1:
                logging.error("Could not add boost to database.")
                dm_channel = message.guild.owner.dm_channel
                if dm_channel == None:
                    dm_channel = await message.guild.owner.create_dm()
                emb.title = f"There was an error adding a boost by '{message.author.display_name}' in '{message.guild.name}'. Please add this boost manually."
                emb.color = get_hex_colour(error=True)
                await dm_channel.send(embed=emb)
                return
            else:
                emb = constructEmbed(message)
                try:
                    await message.channel.send(embed=emb)
                    conn.commit()
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
            c.execute(
                "UPDATE NitroBoosts SET Boosts=?, LatestBoost=? WHERE Guild_ID=? AND User_ID=?",
                (newValue, time, guild_id, booster_id),
            )
            emb = constructEmbed(message, boostAmount)
            try:
                await message.channel.send(embed=emb)
                conn.commit()
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


async def Tracking(message):
    # Command
    # "!c nitro track [start|stop|notice]"
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        arg = message.content.split(" ")[2]
        emb = discord.Embed()
        # print(arg)
        if arg.strip() == "start":
            c.execute(f"SELECT * FROM NitroTrack WHERE Guild_ID={message.guild.id}")
            trackStatus = c.fetchone()
            if trackStatus == None:
                c.execute("INSERT INTO NitroTrack VALUES (?,?)", (message.guild.id, 1))
                conn.commit()
                emb.title = "Nitro boost tracking has been enabled for this server."
                emb.color = get_hex_colour(cora_eye=True)
                await message.channel.send(embed=emb)
                return

            elif trackStatus[1] == 1:
                emb.title = "The nitro tracking is already enabled on this server."
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

        elif arg.strip() == "stop":
            c.execute(f"SELECT * FROM NitroTrack WHERE Guild_ID={message.guild.id}")
            trackStatus = c.fetchone()
            if trackStatus == None:
                c.execute("INSERT INTO NitroTrack VALUES (?,?)", (message.guild.id, 0))
                conn.commit()
                emb.title = "Nitro boost tracking has been disabled for this server."
                emb.color = get_hex_colour(cora_eye=True)
                await message.channel.send(embed=emb)
                return

            elif trackStatus[1] == 0:
                emb.title = "The nitro tracking is already disabled on this server."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

            elif trackStatus[1] == 2 or trackStatus[1] == 1:
                c.execute(
                    f"UPDATE NitroTrack SET Track_YN=0 WHERE Guild_ID={message.guild.id}"
                )
                conn.commit()
                emb.title = "Nitro boost tracking has been enabled for this server."
                emb.color = get_hex_colour(cora_eye=True)
                await message.channel.send(embed=emb)
                return

        elif arg.strip() == "notice":
            c.execute(f"SELECT * FROM NitroTrack WHERE Guild_ID={message.guild.id}")
            trackStatus = c.fetchone()
            if trackStatus == None:
                c.execute("INSERT INTO NitroTrack VALUES (?,?)", (message.guild.id, 2))
                conn.commit()
                emb.title = "Nitro boosts will now only be announced on this server."
                emb.color = get_hex_colour(cora_eye=True)
                await message.channel.send(embed=emb)
                return

            elif trackStatus[1] == 2:
                emb.title = "The nitro tracking is already disabled on this server."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

            elif trackStatus[1] == 0 or trackStatus[1] == 1:
                c.execute(
                    f"UPDATE NitroTrack SET Track_YN=2 WHERE Guild_ID={message.guild.id}"
                )
                conn.commit()
                emb.title = "Nitro boosts will now only be announced on this server."
                emb.color = get_hex_colour(cora_eye=True)
                await message.channel.send(embed=emb)
                return


async def addNitro(message):
    # command structure
    # !c nitro add [@user or id], [amount], [time ONLY DATE!! as DD.MM.YYYY]
    # if time is omitted, use current time
    prefix = "!c nitro add "
    args = message.content[len(prefix) :].split(" ")

    emb = discord.Embed()

    try:
        user_raw = args[0]
        boostAmount = int(args[1])
    except Exception:
        emb.title = "Invalid user ID or boost amount. Give user as an ID or a mention. Boost amount should be an integer."
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
        return

    match = MENTION_RE.match(user_raw)
    if match:
        user_id = match.group(1)
        user = message.guild.get_member(int(user_id))
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
        time = args[2]
    except Exception:
        boostTime = datetime.datetime.today().strftime("%d.%m.%Y")
        noTime = 1
    try:
        boostTime = datetime.datetime.strptime(time, "%d.%m.%Y")
    except ValueError:
        if noTime == 0:
            emb.title = (
                "Invalid timeformat. Please give boost time in the format 'DD.MM.YYYY'."
            )
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            return
        else:
            pass

    guild_id = message.guild.id
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
            (guild_id, user.id),
        )
        previousBoosts = c.fetchone()
        if previousBoosts == None:
            c.execute("SELECT Boost_ID FROM NitroBoosts ORDER BY Boost_ID DESC")
            lastID = c.fetchone()
            if lastID == None:
                lastID = 1
            else:
                lastID = lastID[0] + 1

            # Boost_ID INT UNIQUE,
            # User_ID INT,
            # Guild_ID INT,
            # Boost_Time TEXT,
            # LatestBoost TEXT,
            # Boosts INT,
            i = 0
            success = 0
            while i < 10:
                try:
                    c.execute(
                        "INSERT INTO NitroBoosts VALUES (?,?,?,?,?,?)",
                        (lastID, user.id, guild_id, boostTime, boostTime, boostAmount),
                    )
                    success = 1
                    break
                except sqlite3.IntegrityError:
                    i += 1
                    lastID += 1
            if success != 1:
                logging.error("Could not add boost to database.")
                emb.title = f"There was a database error adding a boost by '{user.display_name}'. Please try again later."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return
            emb.description = (
                f"Added {boostAmount} boost(s) by {user.display_name} into database."
            )
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
            newValue = boosts + boostAmount
            # TODO Compare the times of boosts and only update if necessary (either latest or first boost)
            c.execute(
                "UPDATE NitroBoosts SET Boosts=?, LatestBoost=? WHERE Guild_ID=? AND User_ID=?",
                (newValue, time, guild_id, user.id),
            )
            emb.description = (
                f"Added {boostAmount} boost(s) by {user.display_name} into database."
            )
            emb.color = get_hex_colour(cora_eye=True)
            conn.commit()
            await message.channel.send(embed=emb)


async def delNitro(message):
    pass


async def nitroHelp(message):
    emb = discord.Embed()
    emb.title = "Nitro Tracking"
    emb.color = get_hex_colour(cora_blonde=True)
    txt = "**General info**\n\
        This is the best implementation of nitro tracking that is possible within Discord limitations.\n\
        It can track boost amount, times, and boosters. HOWEVER, it cannot continuously check if the boosts are valid. Checks are made either \n\
        automatically when '!c nitro spin' command is used or when using '!c nitro check' manually. These commands however can only see overall Nitro status of the user.\n\
        It cannot see wheter individual boosts have expired, only if all of them have. Please see these commands below for more info.\n\
        **NOTE!!** All commands below require administrator priviledges.\n\
        \n**Enabling/Disabling nitro tracking on server**\n\
        To enable nitro tracking on your server, use\n\
        ```!c nitro start```\n\
        To ONLY show boost announcements but not track boosts, use\n\
        ```!c nitro notice```\n\
        To stop tracking or announcements, use\n\
        ```!c nitro stop```\n\n\
        **Adding boosts manually**\n\
        If you have older boosts active on the server, or an error occured during tracking, you can add them manually to the bot's database by using\n\
        ```!c nitro add [user], [amount], [date]```\n\
        _Arguments:_\n\
        _user_: Spesifies who the booster is. This can be a mention (@user) or a user ID as an integer.\n\
        _amount_: The amount of boosts to add as an integer.\n\
        _date_: The date of the boost(s). This argument is optional. If it is not given, current date will be used.\n\
        \tIf the user is not in the database, this will be added to both the latest and first boost dates. Otherwise the date is compared to the dates\n\
        already in the database and figure out which one to update.\n\
        "
    await message.channel.send(embed=emb)


async def nitroJunction(message):
    if message.author.guild_permissions.administrator:
        try:
            arg2 = message.content.split(" ")[2]
            if arg2.strip() in ["start", "stop", "notice"]:
                await Tracking(message)
            elif arg2.strip() == "add":
                await addNitro(message)
            else:
                await message.channel.send(
                    "Unknown argument. Use '!c nitro help' for correct syntax."
                )
        except IndexError:
            await message.channel.send(
                "No arguments given. Use '!c nitro help' for correct syntax."
            )
    else:
        emb = discord.Embed()
        emb.description = "You do not have the permissions to use this."
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)