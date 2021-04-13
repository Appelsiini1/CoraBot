# CoraBot
# Copyright 2021 (c) Appelsiini1


import discord
import logging

# import tweepy

# scripts, functions & constants
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

logging.basicConfig(
    filename="Coralog.txt",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S",
)
client = discord.Client()
common.initializeDatabase()

# twitter_auth = tweepy.AppAuthHandler(Twit_API_key, Twit_API_secret)


@client.event
async def on_ready():
    print(f"{client.user} {VERSION} is online & ready.")
    logging.info(f"{client.user} {VERSION} is online & ready.")


# main event, parses commands
@client.event
async def on_message(message):
    if message.author == client.user:
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
        print("sairasta")
        msg = "https://cdn.discordapp.com/attachments/693166291468681227/823282434203189258/eioonormaalii.gif"
        await message.channel.send(msg)
        return
    elif message.content.startswith(PREFIX) == False:
        return
    elif message.type in [
        discord.MessageType.premium_guild_subscription,
        discord.MessageType.premium_guild_tier_1,
        discord.MessageType.premium_guild_tier_2,
        discord.MessageType.premium_guild_tier_3,
    ]:
        nitro.trackNitro(message)

    cmd = message.content.split(" ")[1]

    if cmd == "hi" or cmd == "hello":
        await message.channel.send("Hello!")
    elif cmd == "help":
        await commands.cmds(message)
    elif cmd == "author":
        await message.channel.send(AUTHOR)
    elif cmd == "git":
        await message.channel.send(GIT)
    elif cmd == "version":
        await message.channel.send(f"CoraBot {VERSION}")
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
        await giveaway.end_giveaway(message, client.user.id)
    elif cmd == "vacc":
        await vaccine.sendVaccInfo(message)
    elif cmd == "tirsk":
        await tirsk.tirskCount(message)
    elif cmd == "poll":
        await poll.Poll(message)
    elif cmd == "vote":
        await vote.vote(message)
    elif cmd == "pop":
        await pop.pop(message)
    # elif cmd == "test":
    #     await nitro.test(message)
    elif cmd == "mood":
        await message.channel.send("https://cdn.discordapp.com/attachments/816694548457324544/830847194142605403/hui_saakeli_tata_elamaa.mp4")
    elif cmd == "nitro":
        try:
            arg2 = message.content.split(" ")[2]
            if arg2.strip() in ["start", "stop", "notice"]:
                await nitro.Tracking(message)
            else:
                await message.channel.send("What was that?")
        except IndexError:
            await message.channel.send("Unknown argument. Use '!c nitro help' for correct syntax.")

    else:
        await message.channel.send("What was that?")


client.run(DISCORD_TOKEN)