from discord.ext import commands
from modules.common import check_if_channel, check_if_bot
import requests
import json
import logging


class Insult(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(check_if_channel)
    @commands.check(check_if_bot)
    async def insult(self, ctx):
        prefix = "!c insult "
        response = requests.get(
            "https://evilinsult.com/generate_insult.php?lang=en&type=json"
        )
        if response.status_code == 200:
            json_data = json.loads(response.text)
            if len(ctx.message.content.split(" ")) > 2:
                try:
                    mentioned_user = ctx.message.mentions[0].mention
                except IndexError:
                    mentioned_user = ctx.message.content[len(prefix) :]
                quote = "Hey " + mentioned_user + "! " + json_data["insult"]
            else:
                quote = json_data["insult"]

            await ctx.send(quote)
        else:
            msg = "Could not fetch insult, server responded with code {}".format(
                response.status_code
            )
            logging.error(msg)
            await ctx.send(msg)


def setup(client):
    client.add_cog(Insult(client))