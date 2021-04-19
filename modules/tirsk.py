import discord
import logging
import time
from modules.common import get_hex_colour
from datetime import datetime
import re

MENTION_RE = re.compile(r"^.*<@!(\d+)>")


async def tirskCount(message):
    logging.info("Started quote counting in {}".format(message.channel.name))
    emb = discord.Embed(
        description="_Counting quotes... (this could take a while)_",
        color=get_hex_colour(),
    )
    msgID = await message.channel.send(embed=emb)
    counter = {}
    async for msg in message.channel.history(limit=None):
        time.sleep(0.07)
        mentions = msg.mentions
        if len(mentions) == 0:
            continue
        elif len(mentions) == 1:
            auth = mentions[0].id
            if auth in counter:
                counter[auth] += 1
            else:
                counter[auth] = 1
        elif len(mentions) >= 2:
            # pos = msg.content.rfind("<")
            # user_id = msg.content[pos:].strip()[3:][:-1]
            match = MENTION_RE.match(msg.content)
            if match:
                user_id = match.group(1)
                user = await message.guild.fetch_member(int(user_id))
                auth = user.id
                if auth in counter:
                    counter[auth] += 1
                else:
                    counter[auth] = 1

    txt = ""
    c_time = datetime.today().strftime("%d.%m.%Y")
    for keypair in sorted(counter.items(), key=lambda x: x[1], reverse=True):
        name = await message.guild.fetch_member(keypair[0])
        time.sleep(0.07)
        if name:
            name = name.display_name
        else:
            name = keypair[0]
        txt += f"{name}: {keypair[1]}\n"
    emb.title = f"Quote Scoreboard {c_time}:"
    emb.description = txt
    await msgID.edit(embed=emb)
    logging.info("Quote counting in {} finished.".format(message.channel.name))