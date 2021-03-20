import discord
import os
import sys

# import scripts
from modules import common
from modules import quote
from modules import insult
from modules import commands
from modules import choose


PREFIX = "!c "

author = "This bot is maintained by Appelsiini1"
git = "This will have the GitHub link to the source code later."

client = discord.Client()
tokens = common.get_tokens()
discordToken = tokens[0].lstrip("TOKEN").strip()[1:]
try:
    exit_code = tokens[4].lstrip("EXIT_CODE").strip()[1:]
except IndexError:
    print("Exit code has not been set in .env, exit command has been disabled.")
    exit_code = 0

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

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
        await message.channel.send(author)
    elif cmd == "git":
        await message.channel.send(git)
    elif cmd == "inspire":
        await quote.get_quote(message)
    elif cmd == "insult":
        await insult.insult(message)
    elif cmd == "choose":
        await choose.choose(message)


    #elif cmd == "embed":
    #    await embed_test.test_embed(message)

    else:
        await message.channel.send("What was that?")

client.run(discordToken)
