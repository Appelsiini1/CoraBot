import discord
import logging

# import tweepy

# import scripts
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

# TODO Commit viestin lähetystä ennen

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
    print("{0.user} is online & ready.".format(client))
    logging.info("{0.user} is online & ready.".format(client))


# main event, parses commands
@client.event
async def on_message(message):
    if message.author == client.user:
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

    cmd = message.content.split(" ")[1]

    if cmd == "hi" or cmd == "hello":
        await message.channel.send("Hello!")
    elif cmd == "help":
        await commands.cmds(message)
    elif cmd == "author":
        await message.channel.send(AUTHOR)
    elif cmd == "git":
        await message.channel.send(GIT)
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

    else:
        await message.channel.send("What was that?")


client.run(DISCORD_TOKEN)
