from discord import Embed
from discord.errors import Forbidden
from discord.ext import commands
from modules.common import forbiddenErrorHandler, get_hex_colour, check_if_channel, check_if_bot


class Pop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(check_if_channel)
    @commands.check(check_if_bot)
    async def pop(self, ctx):
        # Command structure
        # !c pop [integer]
        emb = Embed()
        try:
            arg = int(ctx.message.content.split(" ")[2].strip().lstrip("[").rstrip("]"))
        except Exception:
            emb.description = "Invalid argument. Argument must be an integer."
            emb.color = get_hex_colour(error=True)
            try:
                await ctx.send(embed=emb)
            except Forbidden:
                await forbiddenErrorHandler(ctx.message)
            return

        if arg > 14:
            emb.description = "The pop is too thick! The maximum I can do is 14!"
            emb.color = get_hex_colour(error=True)
            await ctx.send(embed=emb)
            return

        pop = ""
        x = 0
        y = 0
        while x < arg:
            while y < arg:
                pop += "||pop!||"
                y += 1
            x += 1
            y = 0
            pop += "\n"

        try:
            await ctx.send(pop)
        except Forbidden:
            await forbiddenErrorHandler(ctx.message)


def setup(client):
    client.add_cog(Pop(client))