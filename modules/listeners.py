import discord
from discord.ext.commands import Bot
from modules import common
import logging
from constants import VERSION
from datetime import datetime

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

async def on_ready():
    print(f"{Bot.user.name} {VERSION} is online & ready.")
    logging.info(f"{Bot.user.name} {VERSION} is online & ready.")

