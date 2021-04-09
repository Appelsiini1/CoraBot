from discord import Embed
from modules.common import get_hex_colour

async def pop(message):
    # Command structure
    # !c pop [integer]
    emb = Embed()
    try:
        arg = int(message.content.split(" ")[2].strip().lstrip("[").rstrip("]"))
    except Exception:
        emb.description = "Invalid argument. Argument must be an integer."
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
        return

    if arg > 14:
        emb.description = "The pop is too thick! The maximum I can do is 14!"
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
        return

    pop = ""
    x = 0
    y = 0
    while x<arg:
        while y<arg:
            pop += "||pop!||"
            y += 1
        x += 1
        y = 0
        pop += "\n"

    await message.channel.send(pop)