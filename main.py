import discord
import os
import sys

# import scripts
from modules import quote


PREFIX = "!c "
TOKEN = "ODIyMjE2ODQ5NDg3Mjk4NTkz.YFPDHA.TYgb7wI4bUvNZN-QoIqA5QkD-gM"

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

if os.getenv('TOKEN') == None:
    try:
        with open(".env", "r") as f:
            tokens = f.readlines()
    except Exception:
        print("Could not acquire environment variables. Stopping.")
        sys.exit(1)
    discordToken = tokens[0].lstrip("TOKEN").strip()[1:]
    client.run(TOKEN)

else:   
    client.run(os.getenv('TOKEN'))
