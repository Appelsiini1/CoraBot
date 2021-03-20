import discord
from modules import common

async def cmds(message):
    cmd_list = """List of available commands:
hi (alias: hello)
help
author
git
inspire
insult [user]"""
    emb = discord.Embed(description=cmd_list, colour=common.get_hex_colour(cora_blonde=True))
    await message.channel.send(embed=emb)