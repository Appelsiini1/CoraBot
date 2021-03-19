import discord
import os

# import scripts
from modules import quote


PREFIX = "!c "

client = discord.Client()

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
    elif cmd == "inspire":
        await quote.get_quote(message)


    else:
        await message.channel.send("What was that?")


client.run(os.getenv('TOKEN').strip("[]"))