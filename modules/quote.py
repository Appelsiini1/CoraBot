from discord.errors import Forbidden
from discord.ext import commands
import requests
import json
from modules.common import forbiddenErrorHandler, get_hex_colour
import logging
from discord import Embed


class Inspire(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="inspire")
    async def get_quote(self, ctx):
        try:
            response = requests.get("https://zenquotes.io/api/random")
        except Exception as e:
            logging.exception("Request for inspire failed.")
            msg = f"Could not get a quote because of a network error."
            emb = Embed(description=msg, color=get_hex_colour(error=True))
            try:
                await ctx.send(embed=emb)
            except Forbidden:
                await forbiddenErrorHandler(ctx.message)
            return

        if response.status_code == 200:
            json_data = json.loads(response.text)
            quote = "_" + json_data[0]["q"] + "_ -" + json_data[0]["a"]
            emb = Embed(description=quote, color=get_hex_colour())
        else:
            msg = "Could not get quote, server responded with code {}".format(
                response.status_code
            )
            logging.error(msg)
            emb = Embed(description=msg, color=get_hex_colour(error=True))

        try:
            await ctx.send(embed=emb)
        except Forbidden:
            await forbiddenErrorHandler(ctx.message)


def setup(client):
    client.add_cog(Inspire(client))