import discord
import logging
import sqlite3
import datetime
from modules.common import get_hex_colour
from constants import DB_F

EMOJI = "\N{PARTY POPPER}"


async def trackNitro(message):
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        guild_id = message.guild.id
        booster_id = message.author.id
        time = datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")
        emb = discord.Embed()

        c.execute(f"SELECT * FROM TrackNitro WHERE Guild_ID={guild_id}")
        track = c.fetchone()
        if track[0][1] == 0 or track == None:
            return
        elif track[0][1] == 2:  # TODO Only post a notice of the boost but do not track
            emb.title = f"{EMOJI} {EMOJI} NEW BOOST! {EMOJI} {EMOJI}"
            emb.color = get_hex_colour(cora_eye=True)
            if message.type == discord.MessageType.premium_guild_subscription:
                emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!"
            elif message.type == discord.MessageType.premium_guild_tier_1:
                emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                    The server has leveled up to Level 1! {EMOJI}"
            elif message.type == discord.MessageType.premium_guild_tier_2:
                emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                    The server has leveled up to Level 2! {EMOJI} {EMOJI}"
            elif message.type == discord.MessageType.premium_guild_tier_3:
                emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                    The server has leveled up to Level 3! {EMOJI} {EMOJI} {EMOJI}"
            try:
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

        c.execute(
            "SELECT * FROM NitroBoosts WHERE Guild_ID=? AND User_ID=?",
            (guild_id, booster_id),
        )
        previousBoosts = c.fetchall()
        if len(previousBoosts) == 0 or previousBoosts == None:
            c.execute("SELECT Boost_ID FROM NitroBoosts ORDER BY Boost_ID DESC")
            lastID = c.fetchone()
            if lastID == None:
                lastID = 1
            else:
                lastID += 1

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
                        (lastID, booster_id, guild_id, time, time, 1),
                    )
                    success = 1
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
                emb.title = f"{EMOJI} {EMOJI} NEW BOOST! {EMOJI} {EMOJI}"
                emb.color = get_hex_colour(cora_eye=True)
                if message.type == discord.MessageType.premium_guild_subscription:
                    emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!"
                elif message.type == discord.MessageType.premium_guild_tier_1:
                    emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                        The server has leveled up to Level 1! {EMOJI}"
                elif message.type == discord.MessageType.premium_guild_tier_2:
                    emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                        The server has leveled up to Level 2! {EMOJI} {EMOJI}"
                elif message.type == discord.MessageType.premium_guild_tier_3:
                    emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                        The server has leveled up to Level 3! {EMOJI} {EMOJI} {EMOJI}"
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
            boosts = boost[0][5]
            newValue = boosts + 1
            c.execute(
                "UPDATE NitroBoosts SET Boosts=?, LatestBoost=? WHERE Guild_ID=? AND User_ID=?",
                (newValue, time, guild_id, booster_id),
            )
            emb.title = f"{EMOJI} {EMOJI} NEW BOOST! {EMOJI} {EMOJI}"
            emb.color = get_hex_colour(cora_eye=True)
            if message.type == discord.MessageType.premium_guild_subscription:
                emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!"
            elif message.type == discord.MessageType.premium_guild_tier_1:
                emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                    The server has leveled up to Level 1! {EMOJI}"
            elif message.type == discord.MessageType.premium_guild_tier_2:
                emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                    The server has leveled up to Level 2! {EMOJI} {EMOJI}"
            elif message.type == discord.MessageType.premium_guild_tier_3:
                emb.description = f"{message.guild.name} just got a new boost by {message.author.display_name}!\n\
                    The server has leveled up to Level 3! {EMOJI} {EMOJI} {EMOJI}"
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
        arg = message.content.split(" ")[3]
        emb = discord.Embed()
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

            elif trackStatus[0][1] == 1:
                emb.title = "The nitro tracking is already enabled on this server."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

            elif trackStatus[0][1] == 2 or trackStatus[0][1] == 0:
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

            elif trackStatus[0][1] == 0:
                emb.title = "The nitro tracking is already disabled on this server."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

            elif trackStatus[0][1] == 2 or trackStatus[0][1] == 1:
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

            elif trackStatus[0][1] == 2:
                emb.title = "The nitro tracking is already disabled on this server."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

            elif trackStatus[0][1] == 0 or trackStatus[0][1] == 1:
                c.execute(
                    f"UPDATE NitroTrack SET Track_YN=2 WHERE Guild_ID={message.guild.id}"
                )
                conn.commit()
                emb.title = "Nitro boosts will now only be announced on this server."
                emb.color = get_hex_colour(cora_eye=True)
                await message.channel.send(embed=emb)
                return


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