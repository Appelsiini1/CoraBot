import logging
from modules.common import forbiddenErrorHandler
from discord.errors import Forbidden
from discord.ext import commands


class PressF(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["f", "F"])
    async def pressF(self, ctx):
        if ctx.guild.id == 181079344611852288:
            emote_name = "cacF"
            try:
                for em in ctx.guild.emojis:
                    if em.name == emote_name:
                        emoji = em
                        break
                msg = str(emoji)
            except Exception as e:
                logging.exception("Exception in !c f when trying to post 'cacF' emoji.")
                msg = "{} has paid their respects.".format(ctx.author.display_name)
        else:
            msg = "{} has paid their respects.".format(ctx.author.display_name)

        try:
            await ctx.send(msg)
        except Forbidden:
            await forbiddenErrorHandler(ctx.message)


def setup(client):
    client.add_cog(PressF(client))
