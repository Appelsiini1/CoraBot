import requests
import json
from modules.common import get_hex_colour #pylint: disable=import-error
import logging
import discord

async def get_quote(message):

    response = requests.get("https://zenquotes.io/api/random")
    if response.status_code == 200:
        json_data = json.loads(response.text)
        quote = "_"+json_data[0]['q'] + "_ -" + json_data[0]['a']
        emb = discord.Embed(description=quote, color=get_hex_colour())
    else:
        msg = "Could not get quote, server responded with code {}".format(response.status_code)
        logging.error(msg)
        emb = discord.Embed(description=msg, color=0xFF0000)

    await message.channel.send(embed=emb)