import discord
import os
import sys
import logging
import tweepy

# import scripts
from modules import common
from modules import quote
from modules import insult
from modules import commands
from modules import choose
from modules import get_tweet


PREFIX = "!c "

AUTHOR = "This bot is maintained by Appelsiini1"
GIT = "Source code for this bot can be found at https://github.com/Appelsiini1/CoraBot"

logging.basicConfig(filename="Coralog.txt", level=logging.INFO, format='%(asctime)s %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
client = discord.Client()
tokens = common.get_tokens()
discordToken = tokens[0].lstrip("TOKEN").strip()[1:]
Twit_API_key = tokens[1].lstrip("API_KEY").strip()[1:]
Twit_API_secret = tokens[2].lstrip("API_SECRET").strip()[1:]

twitter_auth = tweepy.AppAuthHandler(Twit_API_key, Twit_API_secret)

try:
    exit_code = tokens[4].lstrip("EXIT_CODE").strip()[1:]
except IndexError:
    print("Exit code has not been set in .env, exit command has been disabled.")
    exit_code = 0

@client.event
async def on_ready():
    print('{0.user} is online & ready.'.format(client))
    logging.info('{0.user} is online & ready.'.format(client))

# main event, parses commands
@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.content.startswith(PREFIX) == False:
        return
    
    cmd = message.content.split(" ")[1]

    if cmd == "hi" or cmd == "hello":
        await message.channel.send('Hello!')
    elif cmd == "exit":
        if exit_code != 0:
            await common.exit_bot(message, exit_code)
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
    elif cmd == "tweet":
        await get_tweet.get_tweet(message, twitter_auth)

    else:
        await message.channel.send("What was that?")

client.run(discordToken)
