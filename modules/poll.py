import random
import discord
import logging
import sqlite3
import re

from modules.common import get_hex_colour, selectReactionEmoji
from modules.emoji_list import _EMOJIS
from constants import DB_F

_POLL_PREFIX = "!c poll "
MAX_OPTIONS = 20

RoleRE1 = re.compile(r"^.*<@&(\d+)>")


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
        await endPolls(message)
    elif content == "roles":
        if message.author.guild_permissions.administrator:
            await showRoles(message)
        else:
            emb = discord.Embed()
            emb.description = "You do not have the permissions to use this."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
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
    elif content == "delroles":
        if message.author.guild_permissions.administrator:
            await delRoles(message)
        else:
            emb = discord.Embed()
            emb.description = "You do not have the permissions to use this."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
    else:
        await sendHelp(message)
    # elif content == "edit": #TODO add an edit command?


async def sendHelp(message):
    emb = discord.Embed()
    emb.title = "How to use polls 1/2"
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
        where [role] is a role ID or a role mention.\n\
        Note that you can also delete all roles with the keyword 'all', as in\n\
        ```!c poll delrole all```"
    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()

    emb.description = txt1
    await dm_channel.send(embed=emb)
    emb.description = txt2
    emb.title = "How to use polls 2/2"
    await dm_channel.send(embed=emb)


async def startBasicPoll(message):
    # Command structure:
    # !c poll new [title]; [option1]; [option2]; ... ; [option20]

    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()

        prefix = _POLL_PREFIX + "new "
        emb = discord.Embed()
        args = message.content[len(prefix) :].split(";")
        title = args[0]
        titleStatus = 0
        del args[0]
        if title.strip() == "":
            title = f"A poll by {message.author.name}"
            titleStatus = 1

        if len(args) <= 1 or message.content.find(";") == -1:
            # help command
            emb.description = "You gave less than 2 options or you are missing separators. For correct use of the command, use ```!c poll help```"
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
        elif len(args) <= 20:
            poll_txt = "React with the emojis listed below to vote on this poll!\n\n**Options:**\n"
            emoji_list = selectReactionEmoji(len(args), indexes=True)
            i = 0
            for option in args:
                emoji = _EMOJIS[emoji_list[i]]
                poll_txt += emoji + ": " + option.strip() + "\n"
                i += 1

            if len(poll_txt) >= 2048:
                emb.description = (
                    "Poll character limit exceeded! Try reducing some characters."
                )
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
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
            txt = "Your basic poll in channel '{0}' of '{1}' with ID {2} was succesfully created with command:".format(
                message.channel.name, message.guild.name, str(msg.id)
            )
            txt2 = "```{}```".format(message.content)

            emoji_str = ""
            for i in emoji_list:
                emoji_str += str(i) + ","
            if titleStatus == 1:
                title = None

            c.execute(
                "INSERT INTO BasicPolls VALUES (?,?,?,?,?,?)",
                (
                    msg.id,
                    message.channel.id,
                    message.guild.id,
                    message.author.id,
                    emoji_str,
                    title,
                ),
            )
            conn.commit()
            logging.info("Added poll {} into BasicPolls database table.".format(msg.id))
            await dm_channel.send(txt)
            await dm_channel.send(txt2)
            try:
                await message.delete()
            except discord.errors.NotFound:
                logging.exception("Could not delete message when creating a basic poll. Message was not found.")
        else:
            emb.description = "Exceeded maximum option amount of 20 options for polls!"
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)


async def BasicPollEndHelper(poll, message):
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
    for keypair in sorted(results.items(), key=lambda x: x[1], reverse=True):
        if i == 0:
            txt += f"{keypair[0]}** : _{keypair[1]-1}_**\n"
        else:
            txt += f"{keypair[0]} : {keypair[1]-1}\n"
        i += 1

    emb.description = txt
    return emb


# ######################################################################################################## #


async def endPolls(message):
    # Command structure:
    # !c poll end [poll_ID]

    # TODO Consolidate RolePoll and BasicPoll ending under this function

    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()

        prefix = _POLL_PREFIX + "end "
        emb = discord.Embed()
        success = 0

        if len(message.content.split(" ")) == 3:
            c.execute(
                "SELECT * FROM BasicPolls WHERE Author_ID=? AND Ch_ID=?",
                (message.author.id, message.channel.id),
            )
            polls = c.fetchall()
            if len(polls) == 0:
                c.execute(
                    "SELECT * FROM RolePolls WHERE Author_ID=? AND Ch_ID=?",
                    (message.author.id, message.channel.id),
                )
                poll = c.fetchall()
                if len(poll) == 0:
                    emb.description = "There are no polls running that have been initiated by you on this channel."
                    emb.color = get_hex_colour(error=True)
                    await message.channel.send(embed=emb)
                else:
                    polls = await rolePollEndHelper(message, c, polls=poll)
                    if polls != 0:
                        for poll_id in polls:
                            c.execute(f"DELETE FROM RolePolls WHERE Poll_ID={poll_id}")
                        conn.commit()
                        success = 1
                    else:
                        success = 0

            else:
                for poll in polls:
                    emb = await BasicPollEndHelper(poll, message)
                    await message.channel.send(embed=emb)
                c.execute(
                    "DELETE FROM BasicPolls WHERE Author_ID=? AND Ch_ID=?",
                    (message.author.id, message.channel.id),
                )
                # TODO Error handling for basic poll end helper
                conn.commit()
                logging.info(
                    f"{len(polls)} poll(s) by {message.author.name} succesfully ended in {message.channel.name}"
                )
                success = 1
                c.execute(
                    "SELECT * FROM RolePolls WHERE Author_ID=? AND Ch_ID=?",
                    (message.author.id, message.channel.id),
                )
                poll = c.fetchall()
                if len(poll) != 0:
                    polls = await rolePollEndHelper(message, c, polls=poll)
                    if polls != 0:
                        for poll_id in polls:
                            c.execute(f"DELETE FROM RolePolls WHERE Poll_ID={poll_id}")
                        conn.commit()
                        success = 1
                    else:
                        success = 0
        else:
            try:
                arg = int(message.content.split(" ")[3].strip().lstrip("[").rstrip("]"))
            except Exception:
                logging.exception(
                    "Something went wrong when trying to convert poll ID to int"
                )
                txt = "\N{no entry} Invalid poll ID!"
                await message.channel.send(txt)
                return

            c.execute(
                "SELECT * FROM BasicPolls WHERE Author_ID=? AND Ch_ID=? AND Poll_ID=?",
                (message.author.id, message.channel.id, arg),
            )
            poll = c.fetchall()
            if len(poll) == 0:
                c.execute(
                    "SELECT * FROM RolePolls WHERE Author_ID=? AND Ch_ID=? AND Poll_ID=?",
                    (message.author.id, message.channel.id, arg),
                )
                poll = c.fetchall()
                if len(poll) == 0:
                    emb.color = get_hex_colour(error=True)
                    emb.description = f"Unable to find poll with ID '{arg}'.\nPlease check that you gave the right ID and you are on the same channel as the poll."
                    await message.channel.send(embed=emb)
                else:
                    polls = await rolePollEndHelper(message, c, poll=poll)
                    if polls != 0:
                        for poll_id in polls:
                            c.execute(f"DELETE FROM RolePolls WHERE Poll_ID={poll_id}")
                        conn.commit()
                        success = 1
                    else:
                        success = 0
            else:
                emb = await BasicPollEndHelper(poll[0], message)
                await message.channel.send(embed=emb)
                c.execute(
                    "DELETE FROM BasicPolls WHERE Author_ID=? AND Ch_ID=? AND Poll_ID=?",
                    (message.author.id, message.channel.id, arg),
                )
                conn.commit()
                logging.info(
                    f"Poll by {message.author.name} succesfully ended in {message.channel.name}"
                )
                success = 1
                c.execute(
                    "SELECT * FROM RolePolls WHERE Author_ID=? AND Ch_ID=?",
                    (message.author.id, message.channel.id),
                )
                poll = c.fetchall()
                if len(poll) != 0:
                    polls = await rolePollEndHelper(message, c, polls=poll)
                    if polls != 0:
                        for poll_id in polls:
                            c.execute(f"DELETE FROM RolePolls WHERE Poll_ID={poll_id}")
                        conn.commit()
                        success = 1
                    else:
                        success = 0
    if success == 1:
        try:
            await message.delete()
        except Exception as e:
            logging.exception("Poll ending command message deletion failed.")


# ######################################################################################################## #


async def recordRoles(message):
    # Command format
    # !c poll setroles [role]:[voteamount],[role]:[voteamount] : ...
    prefix = _POLL_PREFIX + "setroles "
    emb = discord.Embed()
    args = message.content[len(prefix) :].split(",")

    if args == 0:
        emb.description = (
            "You did not give any arguments. Use '!c poll help' for the correct syntax."
        )
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
        return

    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()

        c.execute(
            f"SELECT Role_ID FROM RolesMaxVotes WHERE Guild_ID={message.guild.id}"
        )
        RolesInDB = c.fetchall()

        added = {}
        updated = {}
        roles = message.guild.roles
        roles_dic = {}
        for r in roles:
            roles_dic[r.id] = r.name

        for arg in args:
            try:
                role = arg.split(":")[0].strip().lstrip("[").rstrip("]")
                amount = int(arg.split(":")[1].strip().lstrip("[").rstrip("]"))
                if len(role) == 0:
                    continue
            except Exception:
                emb.description = "Invalid arguments, role must be an ID or a mention and amount must be an integer. \nAlso make sure you have commas and colons in the right place."
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

            # parse mention
            match = RoleRE1.match(role)
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
                return

            roleT = (role_int,)
            if roleT in RolesInDB:
                c.execute(
                    "UPDATE RolesMaxVotes SET MaxVotes=?, Role_name=? WHERE Role_ID=?",
                    (amount, roles_dic[role_int], role_int),
                )
                updated[role_int] = amount
            else:
                try:
                    c.execute(
                        "INSERT INTO RolesMaxVotes VALUES (?,?,?,?)",
                        (role_int, roles_dic[role_int], message.guild.id, amount),
                    )
                except sqlite3.IntegrityError:
                    emb.description = "Error adding roles to database. Aborting."
                    emb.color = get_hex_colour(error=True)
                    await message.channel.send(embed=emb)
                    return
                added[role_int] = amount
        txt1 = "**Following roles & vote amounts were set:**\n"
        txt2 = "**Following roles & vote amounts were updated:**\n"
        comb = ""

        if len(added) > 0:
            for role in added.items():
                txt1 += f"{roles_dic[role[0]]} : {role[1]}\n"
            comb += txt1

        if len(updated) > 0:
            for role in updated.items():
                txt2 += f"{roles_dic[role[0]]} : {role[1]}\n"
            if len(comb) > 0:
                comb += f"\n{txt2}"
            else:
                comb += txt2

        # TODO Add checks for message length
        conn.commit()
        emb.description = comb
        emb.colour = get_hex_colour()
        await message.channel.send(embed=emb)


async def showRoles(message):
    # Command format
    # !c poll roles

    emb = discord.Embed()

    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        c.execute(
            f"SELECT Role_name, MaxVotes FROM RolesMaxVotes WHERE Guild_ID={message.guild.id}"
        )
        onRecord = c.fetchall()
        if len(onRecord) == 0:
            txt = "You do not have any roles on database for this server."
        else:
            txt = ""
            for role in onRecord:
                txt += f"{role[0]} : {role[1]}\n"

        # TODO Add text lenght check
        emb.description = txt
        emb.title = "Following roles & vote amounts are in the database:"
        emb.color = get_hex_colour()
    await message.channel.send(embed=emb)


async def delRoles(message):
    # Command format
    # !c poll delroles [role],[role], ...
    prefix = _POLL_PREFIX + "delroles "
    emb = discord.Embed()
    args = message.content[len(prefix) :].split(",")

    if args[0].strip() == "":
        emb.description = "**You did not give any arguments. Use '!c poll help' for the correct syntax.**"
        emb.color = get_hex_colour(error=True)
        await message.channel.send(embed=emb)
        return

    i = 0
    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()

        if args[0].strip().lstrip("[").rstrip("]") == "all":
            c.execute(f"DELETE FROM RolesMaxVotes WHERE Guild_ID={message.guild.id}")
            i = -1
        else:
            for arg in args:
                match = RoleRE1.match(arg)
                if match:
                    role_id = match.group(1).strip()
                else:
                    role_id = arg.strip()

                try:
                    role_int = int(role_id)
                except ValueError:
                    emb.description = "Invalid arguments, role must be an ID integer or a mention. \nAlso make sure you have commas in the right place."
                    emb.color = get_hex_colour(error=True)
                    await message.channel.send(embed=emb)
                    return
                c.execute(
                    "DELETE FROM RolesMaxVotes WHERE Role_ID=? AND Guild_ID=?",
                    (role_int, message.guild.id),
                )
                i += 1
        conn.commit()
        if i == -1:
            i = "all"
        emb.description = f"Deleted {i} roles from database."
        emb.color = get_hex_colour(cora_eye=True)
        await message.channel.send(embed=emb)


async def startRolePoll(message):
    # Command structure:
    # !c poll new -r [title]; [option1]; [option2]; ... ; [option20]

    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()
        g_id = message.guild.id
        c.execute(f"SELECT * FROM RolesMaxVotes WHERE Guild_ID={g_id}")
        roles = c.fetchall()

        emb = discord.Embed()
        emb2 = discord.Embed()
        poll_colour = get_hex_colour()
        if len(roles) < 1:
            emb.description = "You have not set the maximum vote amounts for roles. See '!c poll help' for more."
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
            return

        prefix = _POLL_PREFIX + "new -r "

        args = message.content[len(prefix) :].split(";")
        title = args[0].strip().lstrip("[").rstrip("]")
        titleStatus = 0
        del args[0]
        if title.strip().lstrip("[").rstrip("]") == "":
            title = f"A poll by {message.author.name}"
            titleStatus = 1

        c.execute("SELECT Poll_ID FROM RolePolls ORDER BY Poll_ID DESC")
        prevPollID = c.fetchone()

        if prevPollID == None:
            poll_id = 100
        else:
            poll_id = prevPollID[0] + 1

        if len(args) <= 1 or message.content.find(";") == -1:
            # help command
            emb.description = "You gave less than 2 options or you are missing separators. For correct use of the command, use ```!c poll help```"
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)
        elif len(args) <= MAX_OPTIONS:
            poll_txt = "Use '!c vote' -command to vote in this poll! See below the poll for an example.\n\n**Options:**\n"
            option_str = ""
            
            i = 1
            for o in args:
                option = o.strip().lstrip("[").rstrip("]")
                if option == "":
                    continue
                option_str += option + ";"
                poll_txt += f"**{str(i)}**: {option}\n"
                i += 1
            numberOfOptions = i-1

            if len(poll_txt) >= 2048:
                emb.description = (
                    "Poll character limit exceeded! Try reducing some characters."
                )
                emb.color = get_hex_colour(error=True)
                await message.channel.send(embed=emb)
                return

            emb.description = poll_txt
            emb.color = poll_colour
            emb.title = title
            footer = "Poll ID: " + str(poll_id)
            emb.set_footer(text=footer)

            dm_channel = message.author.dm_channel
            if dm_channel == None:
                dm_channel = await message.author.create_dm()

            if titleStatus == 1:
                title = None

            i = 0
            success = 0
            while i < 5:
                try:
                    c.execute(
                        "INSERT INTO RolePolls VALUES (?,?,?,?,?,?)",
                        (
                            poll_id,
                            message.channel.id,
                            message.guild.id,
                            message.author.id,
                            option_str,
                            title,
                        ),
                    )
                    success = 1
                    break
                except sqlite3.IntegrityError:
                    poll_id += 1
                    i += 1
                    emb.set_footer(text=f"Poll ID: {poll_id}")
                    continue
            if success != 1:
                emb2.title = (
                    "Poll creation failed due to a database error. Please try again."
                )
                emb2.description = f"Your command was: ```{message.content}```"
                emb2.color = get_hex_colour(error=True)
                await dm_channel.send(embed=emb2)
                return

            txt = "Your advanced poll in channel '{0}' of '{1}' with ID {2} was succesfully created with command:".format(
                message.channel.name, message.guild.name, poll_id
            )
            txt2 = "```{}```".format(message.content)

            if numberOfOptions == 2:
                option1 = 1
                option2 = 2
            else:
                option1 = random.randint(1, numberOfOptions)
                option2 = random.randint(1, numberOfOptions)
                if option2 == option1 and option2 != numberOfOptions:
                    option2 += 1
                elif option2 == option1 and option1-1 != 0:
                    option2 -= 1
                else:
                    option1 = 1
                    option2 = 2

            txt3 = "Here's an example of a vote command that gives {0} vote(s) to option number \
                {1} and {2} vote(s) to option number {3} in this poll.\
                ```!c vote {4} {1}:{0}, {3}:{2}```\
                \nFor more help, use '!c vote help'".format(
                random.randint(1, 5),
                option1,
                random.randint(1, 5),
                option2,
                poll_id,
            )
            emb2.title = "How to vote in this poll:"
            emb2.description = txt3
            emb2.color = poll_colour

            conn.commit()
            await message.channel.send(embed=emb)
            await message.channel.send(embed=emb2)
            logging.info(f"Added poll {poll_id} into RolePolls database table.")
            await dm_channel.send(txt)
            await dm_channel.send(txt2)
            await message.delete()

        else:
            emb.description = (
                f"Exceeded maximum option amount of {MAX_OPTIONS} options for polls!"
            )
            emb.color = get_hex_colour(error=True)
            await message.channel.send(embed=emb)


async def rolePollEndHelper(message, c, poll=None, polls=None):
    emb = discord.Embed()
    poll_ids = []
    if poll != None:
        poll_id = poll[0][0]
        poll_options = poll[0][4][:-1].split(";")
        option_amount = len(poll_options)
        poll_name = poll[0][5]

        c.execute(f"SELECT * FROM RolePolls_Votes WHERE Poll_ID={poll_id}")
        votes = c.fetchall()
        if len(votes) == 0:
            emb.title = f"No votes for '{poll_name}'."
            emb.color = get_hex_colour(cora_blonde=True)
            await message.channel.send(embed=emb)
            poll_ids.append(poll_id)
            return poll_ids
        vote_sums = []
        for i in range(option_amount):
            vote_sums.append(0)
        for vote in votes:
            vote_str = vote[3][:-1].split(";")
            i = 0
            for option in vote_str:
                vote_sums[i] += int(option)
                i += 1

        i = 0
        txt = ""
        for option in vote_sums:
            txt += f"**{poll_options[i]}**: {option}\n"
            i += 1
        poll_ids.append(poll_id)
        emb.description = txt
        emb.title = f"Results for '{poll_name}'"
        emb.color = get_hex_colour(cora_eye=True)
        await message.channel.send(embed=emb)
        return poll_ids

    elif polls != None:
        for poll in polls:
            poll_id = poll[0]
            poll_options = poll[4][:-1].split(";")
            option_amount = len(poll_options)
            poll_name = poll[5]

            c.execute(f"SELECT * FROM RolePolls_Votes WHERE Poll_ID={poll_id}")
            votes = c.fetchall()
            if len(votes) == 0:
                emb.title = f"No votes for '{poll_name}'."
                emb.color = get_hex_colour(cora_blonde=True)
                await message.channel.send(embed=emb)
                poll_ids.append(poll_id)
                continue
            vote_sums = []
            for i in range(option_amount):
                vote_sums.append(0)
            for vote in votes:
                vote_str = vote[3][:-1].split(";")
                i = 0
                for option in vote_str:
                    vote_sums[i] += int(option)
                    i += 1

            i = 0
            txt = ""
            for option in vote_sums:
                txt += f"**{poll_options[i]}**: {option}\n"
                i += 1
            poll_ids.append(poll_id)
            emb.description = txt
            emb.title = f"Results for '{poll_name}'"
            emb.color = get_hex_colour(cora_eye=True)
            await message.channel.send(embed=emb)
        return poll_ids
    return 0
