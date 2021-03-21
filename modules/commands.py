import discord
from modules import common #pylint: disable=import-error

async def cmds(message):
    cmd_list = """List of available commands:
hi (alias: hello)
help
author
git
inspire
insult [user]
tweet [twitter username]

Admin commands:
giveaway
endgiveaway [GiveawayID]"""
    emb = discord.Embed(description=cmd_list, colour=common.get_hex_colour(cora_blonde=True))
    await message.channel.send(embed=emb)