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


def constructEmbed(message, boosts):
    emb = discord.Embed()

    if message.guild.id == 181079344611852288: # TinyCactus easter egg
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
        time = datetime.datetime.today().strftime("%d.%m.%Y %H:%M:%S")
        emb = discord.Embed()

        try:
            boostAmount = int(message.content)
        except Exception:
            boostAmount = 1

        c.execute(f"SELECT * FROM NitroTrack WHERE Guild_ID={guild_id}")
        track = c.fetchone()
        # print(track)
        if track == None:
            print("Here")
            return
        elif track[1] == 2:  # TODO Only post a notice of the boost but do not track
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
    pass


async def parseNitroAddition(message):
    pass


async def delNitro(message):
    pass