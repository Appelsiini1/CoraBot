import random
import discord
from modules.common import get_hex_colour #pylint: disable=import-error

async def choose(message):
    repl = message.content[9:]
    args = repl.strip().split("|")
    valid = [x for x in args if x.strip() != '']

    if len(valid) < 2:
        msg = "**I need at least 2 options! Syntax: [option1] | [option2] ...**"
    else:
        random_n = random.randint(0, len(valid)-1)
        chosen = valid[random_n]
        msg = "**"+ message.author.display_name + ", I choose '" + chosen.strip()+"'!**"
    
    emb = discord.Embed(title=msg, color=get_hex_colour(cora_eye=True))
    await message.channel.send(embed=emb)