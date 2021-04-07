import discord
import logging
import sqlite3
import re

from modules.common import get_hex_colour, selectReactionEmoji, CURR_DIR
from modules.emoji_list import _EMOJIS

_POLL_PREFIX = "!c poll "

RoleRE = re.compile(r"^.*<@&(\d+)>")

async def Poll(message):
    content = message.content.split(" ")[2]
    try:
        arg = message.content.split(" ")[3]
    except IndexError:
        arg = ""

    if content == "help":
        await sendHelp(message)
    elif content == "new" and arg != "-r":
        await startBasicPoll(message)
    elif content == "end":
        await endBasicPoll(message)
    elif content == "new" and arg == "-r":
        if message.author.guild_permissions.administrator:
            await startRolePoll(message)
        else:
            emb = discord.Embed()
            emb.description = "You do not have the permissions to use this."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
    elif content == "setroles":
        if message.author.guild_permissions.administrator:
            await recordRoles(message)
        else:
            emb = discord.Embed()
            emb.description = "You do not have the permissions to use this."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
    else:
        await sendHelp(message)
    #elif content == "edit": #TODO add an edit command?

async def sendHelp(message):
    emb = discord.Embed()
    emb.title = "How to use polls"
    emb.color = get_hex_colour()
    txt1 = "Command usage: ```!c poll [new|end|help]```\n\
        **Adding a new basic poll:**\n\
        ```!c poll new [title]; [option1]; [option2]; ... [option20]```\n\
        The command will select random emotes for reactions. You can leave the title empty, but in that case remember to put a ';' before the first option.\n\
        Please note that the poll has a character limit of about ~1800 to ~1950 characters depending on how many options you have. Title is not counted into this amount.\n\
        \n\
        **Ending a poll:**\n\
        ```!c poll end [Poll ID]```\n\
        _NOTE!_ If you have multiple polls running (basic or advanced), you can end them all by leaving out the ID.\n\
        The command will only end polls that have been iniated by you.\n"
    txt2 = "_**Advanced polls**_\n\
        Please note that advanced polls require administrator permissions to use.\
        With advanced polls you can set different maximum vote amounts for different roles. Voting will be done via a command as opposed to reactions in the basic polls. You can end advanced polls the same command as basic polls.\n\
        To add or edit roles in(to) the bot's database, use \n```!c poll setroles [role]:[voteamount],[role]:[voteamount], ...```\n\
        You can add as many roles as you need. Input the role as a mention (@role) or a role ID if you don't want to mention the role (you can get a role ID by enabling Discord's Developer mode. Then go to 'Server Settings' -> 'Roles' and copy the ID by right clicking on the role and selecting 'Copy ID'. To enable Developer mode, see https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-).\
        'voteamount' should be an integer.\n\
        \n\
        **Adding a new advanced poll:**\
        ```!c poll new -r [title]; [option1]; [option2]; ... [option20]```\n\
        Please note that the poll has a character limit of about ~1800 to ~1950 characters depending on how many options you have. Title is not counted into this amount.\n\
        \n**For voting help, type:**\n\
        ```!c vote help```\n\
        \n\
        **Editing or deleting roles from the database:**\n\
        If you want to change how many votes a role has use:\n\
        ```!c poll editrole [role]:[voteamount],[role]:[voteamount], ...```\n\
        Note, that if you change anything in the role you do not need to add or edit the role in the bot's database unless you delete and create a new role in the server settings.\
        If you wish to delete a role, use\n\
        ```!c poll delrole [role], [role], ...```\n\
        Note that you can delete all roles with the keyword 'all', as in\n\
        ```!c poll delrole all```"
    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()
    
    emb.description = txt1
    await dm_channel.send(embed=emb)
    emb.description = txt2
    await dm_channel.send(embed=emb)

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
    titleStatus = 0
    del args[0]
    if title.strip() == "":
        title = f"A poll by {message.author.name}"
        titleStatus = 1

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
        txt = "Your basic poll in channel '{0}' of '{1}' with ID {2} was succesfully created with command:".format(message.channel.name, message.guild.name, str(msg.id))
        txt2 = "```{}```".format(message.content)

        emoji_str = ""
        for i in emoji_list:
            emoji_str += str(i) + ","
        if titleStatus == 1:
            title = None
        
        c.execute("INSERT INTO BasicPolls VALUES (?,?,?,?,?,?)", (msg.id, message.channel.id, message.guild.id, message.author.id, emoji_str, title))
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

async def pollEndHelper(poll, message):
    emb = discord.Embed()
    emb.color = get_hex_colour()
    # Poll_ID INT UNIQUE, 0
    # Ch_ID INT,      1
    # Guild_ID INT,   2
    # Author_ID INT,  3
    # Emojis TEXT,    4
    # PollName TEXT,  5

    msg = await message.channel.fetch_message(poll[0])
    originalEmojis = poll[4][:-1].split(",")

    emojis = []
    for i in originalEmojis: 
        emojis.append(_EMOJIS[int(i)])

    pollName = poll[5]
    results = {}
    for reaction in msg.reactions:
        if reaction.emoji in emojis:
            results[reaction.emoji] = reaction.count

    if pollName == None:
        emb.title = "Poll results:"
    else:
        emb.title = f"Results for '{pollName}'"

    txt = ""
    i = 0
    for keypair in sorted(results.items(),key=lambda x:x[1], reverse=True):
        if i == 0:
            txt += f"{keypair[0]}** : _{keypair[1]-1}_**\n"
        else:
            txt += f"{keypair[0]} : {keypair[1]-1}\n"
        i += 1

    emb.description = txt
    return emb

async def endBasicPoll(message):
    # Command structure:
    # !c poll end [poll_ID]

    #TODO Consolidate RolePoll and BasicPoll ending under this function

    db_file = CURR_DIR + "\\databases.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    prefix = _POLL_PREFIX + "end "
    emb = discord.Embed()

    if len(message.content.split(" ")) == 3:
        c.execute("SELECT * FROM BasicPolls WHERE Author_ID=? AND Ch_ID=?", (message.author.id, message.channel.id))
        polls = c.fetchall()
        if len(polls) == 0:
            emb.description = "There are no polls running that have been initiated by you on this channel."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)

        else:
            for poll in polls:
                emb = await pollEndHelper(poll, message)
                await message.channel.send(embed=emb)
            c.execute("DELETE FROM BasicPolls WHERE Author_ID=? AND Ch_ID=?", (message.author.id, message.channel.id))
            conn.commit()
            logging.info(f"{len(polls)} poll(s) by {message.author.name} succesfully ended in {message.channel.name}")
    else:
        try:
            arg = int(message.content.split(" ")[3])
        except Exception:
            logging.exception("Something went wrong when trying to convert poll ID to int")
            txt = "\N{no entry} Invalid poll ID!"
            await message.channel.send(txt)
            conn.close()
            return
        
        c.execute("SELECT * FROM BasicPolls WHERE Author_ID=? AND Ch_ID=? AND Poll_ID=?", (message.author.id, message.channel.id, arg))
        poll = c.fetchall()
        if len(poll) == 0:
            emb.color= get_hex_colour(error=True)
            emb.description = f"Unable to find poll with ID '{arg}'"
            await message.channel.send(embed=emb)
        else:
            emb = await pollEndHelper(poll[0], message)
            await message.channel.send(embed=emb)
            c.execute("DELETE FROM BasicPolls WHERE Author_ID=? AND Ch_ID=? AND Poll_ID=?", (message.author.id, message.channel.id, arg))
            conn.commit()
            logging.info(f"Poll by {message.author.name} succesfully ended in {message.channel.name}")
    await message.delete()
    conn.close()

# ######################################################################################################## #   

async def recordRoles(message):
    # Command format
    # !c poll setroles [role]:[voteamount],[role]:[voteamount] : ...
    prefix = _POLL_PREFIX + "setroles "
    emb = discord.Embed()
    args = message.content[len(prefix):].split(",")

    if args == 0:
        emb.description = "You did not give any arguments. Use '!c poll help' for the correct syntax."
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
        return

    db_file = CURR_DIR + "\\databases.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

    c.execute(f"SELECT Role_ID FROM RolesMaxVotes WHERE Guild_ID={message.guild.id}")
    RolesInDB = c.fetchall()

    added = {}
    updated = {}

    for arg in args:
        try:
            role = arg.split(":")[0].strip()
            amount = int(arg.split(":")[1])
            if len(role) == 0:
                continue
        except ValueError:
            emb.description = "Invalid arguments, role must be an ID or a mention and amount must be an integer. \nAlso make sure you have commas and colons in the right place."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            conn.close()
            return

        # parse mention
        match = RoleRE.match(role)
        if match:
            role_id = match.group(1).strip()
        else:
            role_id = role.strip()
        try:
            role_int = int(role_id)
        except ValueError:
            emb.description = "Invalid arguments, role must be an ID integer or a mention and amount must be an integer. \nAlso make sure you have commas and colons in the right place."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            conn.close()
            return

        roleT = (role_int,)
        if roleT in RolesInDB:
            c.execute("UPDATE RolesMaxVotes SET MaxVotes=? WHERE Role_ID=?", (amount, role_int))
            updated[role_int] = amount
        else:
            try:
                c.execute("INSERT INTO RolesMaxVotes VALUES (?,?,?)", (role_int, message.guild.id, amount))
            except sqlite3.IntegrityError:
                emb.description = "Error adding roles to database. Aborting."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return
            added[role_int] = amount
    txt1 = "**Following roles & vote amounts were set:**\n"
    txt2 = "**Following roles & vote amounts were updated:**\n"
    comb = ""
    roles = await message.guild.fetch_roles()

    if len(added) > 0:
        for role in roles:
            if role.id in added:
                # TODO Add SyntaxError check for illegal Unicode emojis
                txt1 += f"'{role.name}' : {added[role.id]}\n"
        comb += txt1

    if len(updated) > 0:
        for role in roles:
            if role.id in updated:
                txt2 += f"'{role.name}' : {updated[role.id]}\n"
        if len(comb) > 0:
            comb += f"\n{txt2}"
        else:
            comb += txt2

    # TODO Add checks for message length
    emb.description = comb
    emb.colour = get_hex_colour()
    await message.channel.send(embed=emb)
    conn.commit()
    conn.close()

async def delRoles(message):
    # Command format
    # !c poll setroles [role],[role], ...
    prefix = _POLL_PREFIX + "setroles "
    emb = discord.Embed()
    args = message.content[len(prefix):].split(",")

    if args == 0:
        emb.description = "You did not give any arguments. Use '!c poll help' for the correct syntax."
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
        return

    db_file = CURR_DIR + "\\databases.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()

async def startRolePoll(message):
    # Command structure:
    # !c poll new -r [title]; [option1]; [option2]; ... ; [option20]

    db_file = CURR_DIR + "\\databases.db"
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    g_id = message.guild.id
    c.execute(f"SELECT * FROM RolesMaxVotes WHERE Guild_ID={g_id}")
    roles = c.fetchall()

    emb = discord.Embed()
    if len(roles) < 1:
        emb.description = "You have not set the maximum vote amounts for roles. See '!c poll help' for more."
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
        return

    prefix = _POLL_PREFIX + "new -r "

    args = message.content[len(prefix):].split(";")
    title = args[0]
    titleStatus = 0
    del args[0]
    if title.strip() == "":
        title = f"A poll by {message.author.name}"
        titleStatus = 1

    if len(args) <= 1 or message.content.find(";") == -1:
        #help command
        emb.description = "You gave less than 2 options or you are missing separators. For correct use of the command, use ```!c poll help```"
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
    elif len(args) <=20:
        poll_txt = "Use '!c vote' -command to vote in this poll! See '!c vote help' for more.\n\n**Options:**\n"
        option_str = ""
        i = 0
        for option in args:
            option_str += option.strip() + ";"
            poll_txt += f"**{str(i+1)}**: {option.strip()}\n"
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

        dm_channel = message.author.dm_channel
        if dm_channel == None:
            dm_channel = await message.author.create_dm()
        txt = "Your advanced poll in channel '{0}' of '{1}' with ID {2} was succesfully created with command:".format(message.channel.name, message.guild.name, str(msg.id))
        txt2 = "```{}```".format(message.content)

        if titleStatus == 1:
            title = None
        
        c.execute("INSERT INTO RolePolls VALUES (?,?,?,?,?,?)", (msg.id, message.channel.id, message.guild.id, message.author.id, option_str, title))
        conn.commit()
        logging.info("Added poll {} into RolePolls database table.".format(msg.id))
        await dm_channel.send(txt)
        await dm_channel.send(txt2)
        await message.delete()

    else:
        emb.description = "Exceeded maximum option amount of 20 options for polls!"
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
    conn.close()

async def rolePollEndHelper():
    pass

async def vote(message):
    pass

async def voteHelp(message):
    emb = discord.Embed()
    emb.color = get_hex_colour()
    emb.title = "Voting in polls"
    emb.description = "You can vote in the _basic polls_ by reacting to the corresponding emote.\n\
    The vote command can be used in _advanced polls_ (indicated by the poll having numbers before the options instead of emotes).\
    **Vote command usage:**\n\
    ```!c vote [Poll ID] [option number]:[amount of votes], [option number]:[amount of votes], ...```\n\
    _NOTE!_ Poll ID can be found in the footer under the poll. You do not need to type the brackets."

    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()
    
    await dm_channel.send(embed=emb)
    await message.delete()