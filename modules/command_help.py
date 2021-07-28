from discord import Embed
from discord.errors import Forbidden
from discord.ext import commands
from discord import MessageType
from discord import ChannelType
import logging
from modules import common
from modules import nitro
from modules import tirsk
from modules import auction
from constants import VERSION, TRACKED_CHANNELS, PREFIX


class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message, *args):
        if message.author.bot == True:
            return
        elif message.type in [
            MessageType.premium_guild_subscription,
            MessageType.premium_guild_tier_1,
            MessageType.premium_guild_tier_2,
            MessageType.premium_guild_tier_3,
        ]:
            await nitro.trackNitro(message)
            return
        elif (
            message.channel.type != ChannelType.text
            and message.channel.type != ChannelType.news
        ):
            return
        elif (
            message.content.find("sairasta") != -1
            or message.content.find("ei oo normaalii") != -1
        ):
            msg = "https://cdn.discordapp.com/attachments/693166291468681227/823282434203189258/eioonormaalii.gif"
            await message.channel.send(msg)
            return
        elif (
            message.channel.id in TRACKED_CHANNELS.channels
            and message.content.startswith(PREFIX) == False
            and message.author != self.bot.user
        ):
            ind = TRACKED_CHANNELS.channels.index(message.channel.id)
            chtype = TRACKED_CHANNELS.types[ind]
            if chtype == 1:
                await tirsk.tirskTrack(message)
                return
            elif chtype == 2:
                await auction.bid(message)
                return

    @commands.command()
    async def help(self, ctx):
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
`saimaa`

**_Admin commands:_**
`giveaway`
`endgiveaway [GiveawayID]`
`poll [set|del]roles`
`poll roles`
`poll new -r`
`nitro [help | add | del | export | start | stop | notice | check | spin]`
    """
        emb = Embed(
            title="List of available commands:",
            description=cmd_list,
            colour=common.get_hex_colour(cora_blonde=True),
        )
        try:
            await ctx.send(embed=emb)
        except Forbidden:
            logging.error("Unable to send message due to 403 - Forbidden")
            emb.clear_fields()
            emb.description = f"Unable to send message to channel in '{ctx.guild.name}'. If you are the server owner, please make sure I have the proper rights to post messages to that channel."
            emb.color = common.get_hex_colour(error=True)
            dm_channel = ctx.guild.owner.dm_channel
            if dm_channel == None:
                dm_channel = await ctx.guild.owner.create_dm()
            await dm_channel.send(embed=emb)

    @commands.command()
    async def info(self, ctx, *arg):
        emb = Embed()
        emb.title = "CoraBot Info"
        emb.description = f"**Created by** Appelsiini1\nThe source code & development info for this bot can be found at https://github.com/Appelsiini1/CoraBot\n\nVersion: {VERSION}"
        emb.color = common.get_hex_colour(cora_blonde=True)
        emb.set_thumbnail(
            url="https://media.discordapp.net/attachments/693166291468681227/834200862246043648/cora_pfp.png"
        )

        try:
            await ctx.send(embed=emb)
        except Forbidden:
            await common.forbiddenErrorHandler(ctx)


def setup(client):
    client.add_cog(Info(client))
