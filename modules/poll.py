import discord
import logging
import sqlite3

from discord import embeds
from modules.common import get_hex_colour, selectReactionEmoji, CURR_DIR
from datetime import datetime

from modules.emoji_list import _EMOJIS

_POLL_PREFIX = "!c poll "

async def Poll(message):
    content = message.content.split(" ")[2]
    if content == "help":
        await sendHelp(message)
    elif content == "new":
        await startBasicPoll(message)
    elif content == "end":
        await endBasicPoll(message)
    else:
        await sendHelp(message)
    #elif content == "edit": #TODO add an edit command?

async def sendHelp(message):
    emb = discord.Embed()
    emb.title = "How to use polls"
    emb.color = get_hex_colour()
    emb.description = "Command usage: ```!c poll [new|end|help]```\n\
        **Adding a new basic poll:**\n\
        ```!c poll new [title]; [option1]; [option2]; ... [option20]```\n\
        The command will select random emotes for reactions. You can leave the title empty, but in that case remember to put a ';' before the first option.\n\
        Please note that the poll has a character limit of about ~1800 to ~1950 characters depending on how many options you have. Title is not counted into this amount.\n\
        \n\
        **Ending a poll:**\n\
        ```!c poll end [Poll ID]```\n\
        _NOTE!_ If you have multiple polls running, you can end them all by leaving out the ID.\n\
        The command will only end polls that have been iniated by you."
    await message.channel.send(embed=emb)

async def startBasicPoll(message):
    # Command structure:
    # !c poll new [title]; [option1]; [option2]; ... ; [option20]

    db_file = CURR_DIR + "\\databases.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    prefix = _POLL_PREFIX + "new "
    emb = discord.Embed()
    args = message.content[len(prefix):].split(";")
    title = args[0]
    del args[0]

    if len(args) <= 1 or message.content.find(";") == -1:
        #help command
        emb.description = "You gave less than 2 options or you are missing separators. For correct use of the command, use ```!c poll help```"
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
    elif len(args) <=20:
        poll_txt = "React with the emojis listed below to vote on this poll!\n\n**Options:**\n"
        emoji_list = selectReactionEmoji(len(args), indexes=True)
        i = 0
        for option in args:
            emoji = _EMOJIS[emoji_list[i]]
            poll_txt += emoji +": " + option.strip() + "\n"
            i += 1

        if len(poll_txt) >= 2048:
            emb.description = "Poll character limit exceeded! Try reducing some characters."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            conn.close()
            return

        emb.description = poll_txt
        emb.color = get_hex_colour()
        emb.title = title
        msg = await message.channel.send(embed=emb)
        footer = "Poll ID: " + str(msg.id)
        emb.set_footer(text=footer)

        await msg.edit(embed=emb)
        for i in emoji_list:
            emoji = _EMOJIS[i]
            await msg.add_reaction(emoji)

        dm_channel = message.author.dm_channel
        if dm_channel == None:
            dm_channel = await message.author.create_dm()
        txt = "Your poll in channel '{0}' of '{1}' with ID {2} was succesfully created with command:".format(message.channel.name, message.guild.name, str(msg.id))
        txt2 = "```{}```".format(message.content)

        emoji_str = ""
        for i in emoji_list:
            emoji_str += str(i) + ","
        
        c.execute("INSERT INTO BasicPolls VALUES (?,?,?,?,?)", (msg.id, message.channel.id, message.guild.id, message.author.id, emoji_str))
        conn.commit()
        logging.info("Added poll {} into BasicPolls database table.".format(msg.id))
        await dm_channel.send(txt)
        await dm_channel.send(txt2)
        await message.delete()
    else:
        emb.description = "Exceeded maximum option amount of 20 options for polls!"
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
    conn.close()


async def endBasicPoll(message):
    # Command structure:
    # !c vote end [poll_ID]

    db_file = CURR_DIR + "\\databases.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    prefix = _POLL_PREFIX + "end "
    emb = discord.Embed()

    if len(message.content.split(" ")) <= 3:
        polls = c.execute("SELECT * FROM BasicPolls")
        if len(polls) == 0:
            emb.description = "You do not have any polls running."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            conn.close()
            return
        else:
            for poll in polls:
                pass
            