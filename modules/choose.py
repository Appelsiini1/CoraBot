import random
import discord
from discord.ext import commands
from modules.common import get_hex_colour
class Choose(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def choose(self, ctx, *arg):
        repl = ctx.message.content[9:]
        args = repl.strip().split("|")
        valid = [x for x in args if x.strip() != ""]

        if len(valid) < 2:
            msg = "**I need at least 2 options! Syntax: `[option1] | [option2] ...`**"
        else:
            random_n = random.randint(0, len(valid) - 1)
            chosen = valid[random_n]
            msg = (
                "**"
                + ctx.author.display_name
                + ", I choose '"
                + chosen.strip()
                + "'!**"
            )

        emb = discord.Embed(title=msg, color=get_hex_colour(cora_eye=True))
        await ctx.send(embed=emb)

def setup(client):
    client.add_cog(Choose(client))