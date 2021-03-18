import requests
import json

async def get_quote(message):
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = "_"+json_data[0]['q'] + "_ -" + json_data[0]['a']
    await message.channel.send(quote)