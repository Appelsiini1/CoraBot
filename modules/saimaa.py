import logging

from discord.errors import Forbidden
from modules.common import forbiddenErrorHandler, get_hex_colour
import discord
import requests

async def saimaa(message):
    await message.channel.trigger_typing()
    response = requests.get("https://wwwi3.ymparisto.fi/i3/tilanne/fin/Lampotila/data/T0411210.txt", headers={"User-Agent": "Appelsiini1:n Discord Botti"},)
    response2 = requests.get("https://wwwi3.ymparisto.fi/i3/tilanne/fin/Lampotila/Lampotila.htm", headers={"User-Agent": "Appelsiini1:n Discord Botti"},)

    if response2.status_code == 200 and response.status_code == 200:
        date = response.text.split("\n")[0].strip().split(";")[0]
        temperature = response.text.split("\n")[0].strip().split(";")[1]
        data2 = response2.text.find("<p>Päivitetty")
        updated = response2.text[data2:][:30].lstrip("<p>Päivitetty ")

        emb = discord.Embed()
        emb.title = "The temperature of the Saimaa lake"
        emb.description = f"The surface temperature as measured in Lauritsala:\n{date}: **{temperature}°C**"
        emb.set_footer(text= f"Source: Finnish Environment Institute (syke.fi)\nUpdated: {updated}")
        emb.color = get_hex_colour()

        try:
            await message.channel.send(embed=emb)
        except Forbidden:
            await forbiddenErrorHandler(message)
    else:
        msg = f"Could not fetch temperature info, response codes {response.status_code} and {response2.status_code}"
        logging.error(msg)
        emb = discord.Embed()
        emb.title = msg
        emb.color = get_hex_colour(error=True)

        try:
            await message.channel.send(embed=emb)
        except Forbidden:
            await forbiddenErrorHandler(message)