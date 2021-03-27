import discord
from modules import common #pylint: disable=import-error

async def cmds(message):
    cmd_list = """hi (alias: hello)
help
author
git
inspire
insult [user]
tweet [twitter username]
f (alias: F)
choose [option1 | option2 | ...]
vacc [Area code (or empty for all areas) | help]

Admin commands:
giveaway
endgiveaway [GiveawayID]"""
    emb = discord.Embed(title="List of available commands:", description=cmd_list, colour=common.get_hex_colour(cora_blonde=True))
    await message.channel.send(embed=emb)