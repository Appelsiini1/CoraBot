import discord
from modules import common


async def cmds(message):
    cmd_list = """hi (alias: hello)
help
author
git
version
inspire
insult [user]
f (alias: F)
choose option1 | option2 | ... 
vacc [Area code (or empty for all areas) | help]
poll [new|end|help]
vote help
vote [Poll ID] [option:votes], [option:votes], ...
pop [number between 1-14]

**_Admin commands:_**
giveaway
endgiveaway [GiveawayID]
poll [set|del]roles
poll roles
poll new -r
nitro [add|del|get|start|stop|notice]
"""
    emb = discord.Embed(
        title="List of available commands:",
        description=cmd_list,
        colour=common.get_hex_colour(cora_blonde=True),
    )
    await message.channel.send(embed=emb)