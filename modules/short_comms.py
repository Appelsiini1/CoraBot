from discord import Embed
from discord.ext import commands
from modules.common import get_hex_colour


class Short(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def hi(self, ctx):
        await ctx.send("Hello!")

    @commands.command()
    async def status(self, ctx):
        emb = Embed()
        emb.color = get_hex_colour()
        emb.title = "CoraBot Status:"
        emb.description = "**418** I'm a teapot"
        await ctx.send(embed=emb)

    @commands.command()
    async def mood(self, ctx):
        await ctx.send(
            "https://cdn.discordapp.com/attachments/816694548457324544/830847194142605403/hui_saakeli_tata_elamaa.mp4"
        )


def setup(client):
    client.add_cog(Short(client))