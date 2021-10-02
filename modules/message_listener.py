from constants import PREFIX, TRACKED_CHANNELS
from discord import ChannelType, MessageType
from discord.ext import commands
from modules import auction, nitro, tirsk

class MESSAGE_LISTENER(commands.Cog):
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

def setup(client):
    client.add_cog(MESSAGE_LISTENER(client))