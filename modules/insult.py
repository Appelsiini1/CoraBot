import requests
import json
import discord
import logging

async def insult(message):
    prefix = "!c insult "
    response = requests.get("https://evilinsult.com/generate_insult.php?lang=en&type=json")
    if response.status_code == 200:
        json_data = json.loads(response.text)
        if len(message.content.split(" ")) > 2:
            try:
                mentioned_user = message.mentions[0].mention
            except IndexError:
                mentioned_user = message.content[len(prefix):]
            quote = "Hey "+mentioned_user+"! " + json_data["insult"]
        else:
            quote = json_data["insult"]

        await message.channel.send(quote)
    else:
        msg = "Could not fetch insult, server responded with code {}".format(response.status_code)
        logging.error(msg)
        await message.channel.send(msg)