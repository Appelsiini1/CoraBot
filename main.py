# CoraBot
# Copyright 2021 (c) Appelsiini1


import discord
import logging
from datetime import datetime, date


# import tweepy

# scripts, functions & constants
from workers import SCHEDULER, CLIENT
from constants import *
from modules import common
from modules import quote
from modules import insult
from modules import commands
from modules import choose
from modules import giveaway
from modules import pressF
from modules import vaccine
from modules import tirsk
from modules import poll
from modules import vote
from modules import pop
from modules import nitro
from modules import dice_comm
from modules import auction


# Initialize required modules and constants
logging.basicConfig(
    filename="Coralog.txt",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)
common.initializeDatabase()

# twitter_auth = tweepy.AppAuthHandler(Twit_API_key, Twit_API_secret)


@CLIENT.event
async def on_ready():
    print(f"{CLIENT.user} {VERSION} is online & ready.")
    logging.info(f"{CLIENT.user} {VERSION} is online & ready.")


@CLIENT.event
async def on_error(event, *args, **kwargs):
    time = datetime.now().strftime("%d.%m.%Y at %H:%M")
    logging.exception(
        f"An unhandled exception occured in {event}. \nMessage: {args[0]}\nMessage content: '{args[0].content}'\n**********"
    )
    print(f"{time} - An unhandled exception occured in {event}, see log for details.")


# main event, parses commands
@CLIENT.event
async def on_message(message):
    if message.author == CLIENT.user:
        return
    elif message.type in [
        discord.MessageType.premium_guild_subscription,
        discord.MessageType.premium_guild_tier_1,
        discord.MessageType.premium_guild_tier_2,
        discord.MessageType.premium_guild_tier_3,
    ]:
        await nitro.trackNitro(message)
        return
    elif (
        message.channel.type != discord.ChannelType.text
        and message.channel.type != discord.ChannelType.news
    ):
        return
    elif (
        message.content.find("sairasta") != -1
        or message.content.find("ei oo normaalii") != -1
    ):
        msg = "https://cdn.discordapp.com/attachments/693166291468681227/823282434203189258/eioonormaalii.gif"
        await message.channel.send(msg)
        return
    elif (
        message.channel.id in TRACKED_CHANNELS.channels
        and message.content.startswith(PREFIX) == False
        and message.author != CLIENT.user
    ):
        ind = TRACKED_CHANNELS.channels.index(message.channel.id)
        chtype = TRACKED_CHANNELS.types[ind]
        if chtype == 1:
            await tirsk.tirskTrack(message)
            return
        elif chtype == 2:
            await auction.bid(message)
            return

    elif message.content.startswith(PREFIX) == False:
        return

    cmd = message.content.split(" ")[1].lower()

    if cmd == "hi" or cmd == "hello":
        await message.channel.send("Hello!")
    elif cmd == "help":
        await commands.cmds(message)
    elif cmd == "author":
        await message.channel.send(AUTHOR)
    elif cmd == "git":
        await message.channel.send(GIT)
    elif cmd == "version":
        await message.channel.send(f"CoraBot `{VERSION}`")
    elif cmd == "inspire":
        await quote.get_quote(message)
    elif cmd == "insult":
        await insult.insult(message)
    elif cmd == "choose":
        await choose.choose(message)
    elif cmd.lower() == "f":
        await pressF.pressF(message)
    elif cmd == "tweet":
        # await get_tweet.get_tweet(message, twitter_auth)
        await message.channel.send("This feature is not yet implemented! Sorry!")
    elif cmd == "giveaway":
        await giveaway.initiate_giveaway(message)
    elif cmd == "endgiveaway":
        await giveaway.end_giveaway(message, CLIENT.user.id)
    elif cmd == "vacc":
        await vaccine.sendVaccInfo(message)
    elif cmd == "tirsk":
        await tirsk.tirskJunction(message)
    elif cmd == "poll":
        await poll.Poll(message)
    elif cmd == "vote":
        await vote.vote(message)
    elif cmd == "pop":
        await pop.pop(message)
    elif cmd == "mood":
        await message.channel.send(
            "https://cdn.discordapp.com/attachments/816694548457324544/830847194142605403/hui_saakeli_tata_elamaa.mp4"
        )
    elif cmd == "nitro":
        await nitro.nitroJunction(message)
    elif cmd == "dice":
        await dice_comm.dice_comm(message)
    elif cmd == "test":
        await SCHEDULER.add_job(auction.testFunction, 'date', run_date=datetime(2021, 5, 19, 21, 30), id="testJob", misfire_grace_time=60, replace_existing=True)
        await message.add_reaction("\N{white heavy check mark}")

    else:
        await message.channel.send("What was that?")


@CLIENT.event
async def on_guild_join(guild):
    emb = discord.Embed()
    emb.color = common.get_hex_colour(cora_blonde=True)
    emb.title = "Hey there!"
    emb.description = "Hi! Thanks for adding me to your server! <3\n\
        You can use my features by typing commands with the prefix `!c`. To access a list of available commands, use `!c help`.\n\
        \nPlease make sure I have the proper rights, especially to view the channels you want me to listen for commands in, send messages & embed links.\n\
        \n\
        Sincerely,\n\
        ~ Cora ~"
    emb.set_thumbnail(
        url="https://media.discordapp.net/attachments/693166291468681227/834200862246043648/cora_pfp.png"
    )
    try:
        dm_channel = guild.owner.dm_channel
        if dm_channel == None:
            dm_channel = await guild.owner.create_dm()
        await dm_channel.send(embed=emb)
    except Exception:
        logging.exception("Could not send welcome message to server owner.")


CLIENT.run(DISCORD_TOKEN)