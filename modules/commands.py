import discord
import logging
from modules import common


async def cmds(message):
    cmd_list = """`hi` (alias: `hello`)
`help`
`info`
`inspire`
`insult [user]`
`f` (alias: `F`)
`choose option1 | option2 | ... `
`vacc [Area code (or empty for all areas) | help]`
`poll [new | end | help]`
`vote help`
`vote [Poll ID] [option:votes], [option:votes], ...`
`pop [number between 1-14]`
`dice [help | [N]dS | [N]wS | [N]uS]` (extra arguments can be seen from dice help)
`status`

**_Admin commands:_**
`giveaway`
`endgiveaway [GiveawayID]`
`poll [set|del]roles`
`poll roles`
`poll new -r`
`nitro [help | add | del | export | start | stop | notice | check | spin]`
"""
    emb = discord.Embed(
        title="List of available commands:",
        description=cmd_list,
        colour=common.get_hex_colour(cora_blonde=True),
    )
    try:
        await message.channel.send(embed=emb)
    except discord.errors.Forbidden:
        logging.error("Unable to send message due to 403 - Forbidden")
        emb.clear_fields()
        emb.description = f"Unable to send message to channel in '{message.guild.name}'. If you are the server owner, please make sure I have the proper rights to post messages to that channel."
        emb.color = common.get_hex_colour(error=True)
        dm_channel = message.guild.owner.dm_channel
        if dm_channel == None:
            dm_channel = await message.guild.owner.create_dm()
        await dm_channel.send(embed=emb)