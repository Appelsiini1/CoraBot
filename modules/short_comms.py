from discord import Embed
from discord.errors import Forbidden
from discord.ext import commands
from modules.common import forbiddenErrorHandler, get_hex_colour


class Short(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["hello"])
    async def hi(self, ctx):
        if ctx.invoked_with == "hi":
            try:
                await ctx.send("Hello!")
            except Forbidden:
                forbiddenErrorHandler(ctx.message)
        else:
            try:
                await ctx.send("Hi!")
            except Forbidden:
                forbiddenErrorHandler(ctx.message)

    @commands.command()
    async def status(self, ctx):
        emb = Embed()
        emb.color = get_hex_colour()
        emb.title = "CoraBot Status:"
        emb.description = "**418** I'm a teapot"
        try:
            await ctx.send(embed=emb)
        except Forbidden:
            forbiddenErrorHandler(ctx.message)

    @commands.command()
    async def mood(self, ctx):
        try:
            await ctx.send(
                "https://cdn.discordapp.com/attachments/816694548457324544/830847194142605403/hui_saakeli_tata_elamaa.mp4"
            )
        except Forbidden:
            forbiddenErrorHandler(ctx.message)


def setup(client):
    client.add_cog(Short(client))