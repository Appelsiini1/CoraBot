import discord
import sqlite3
import logging

from modules.common import get_hex_colour
from constants import DB_F


async def vote(message):
    # Command structure
    # !c vote [Poll ID] [option number]:[amount of votes], [option number]:[amount of votes], ...

    try:
        arg = message.content.split(" ")[2]
    except IndexError:
        arg = ""

    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()
    emb = discord.Embed()

    if arg == "":
        await voteHelp(message)
    elif arg.strip() == "help":
        await voteHelp(message)
    elif arg.strip() == "delete":
        await delVotes(message)
    else:
        try:
            poll_id = int(arg.strip().lstrip("[").rstrip("]"))
        except ValueError:
            await voteErrorHandler(message, dm_channel, 1)  # invalid Poll ID
            return

        with sqlite3.connect(DB_F) as conn:
            prefix = "!c vote " + arg
            args = message.content[len(prefix) :].split(",")
            c = conn.cursor()

            c.execute(
                "SELECT * FROM RolePolls WHERE Poll_ID=? AND Guild_ID=?",
                (poll_id, message.guild.id),
            )
            poll = c.fetchall()
            if len(poll) == 0:
                await voteErrorHandler(message, dm_channel, 2)  # no poll exists with poll ID
                return
            else:
                c.execute(
                    f"SELECT * FROM RolesMaxVotes WHERE Guild_ID={message.guild.id}"
                )
                VoteRoles = c.fetchall()
                MemberRoles = message.author.roles

                roleIDList = []
                foundRoles = []
                for r in MemberRoles:
                    roleIDList.append(r.id)

                for role in VoteRoles:
                    if role[0] in roleIDList:
                        foundRoles.append(role)
                if len(foundRoles) == 0:
                    await voteErrorHandler(
                        message, dm_channel, 3, poll_name=poll[0][5]
                    )  # user does not have roles that can vote
                    return
                else:
                    maxvoteint = 0
                    for role in foundRoles:
                        if role[3] > maxvoteint:
                            maxvoteint = role[3]
                    if maxvoteint == 0:
                        await voteErrorHandler(message, dm_channel, 4)  # user has zero votes
                        return
            c.execute(
                "SELECT * FROM RolePolls_Votes WHERE Voter_ID=? AND Poll_ID=?",
                (message.author.id, poll_id),
            )
            previousVotes = c.fetchall()
            if len(previousVotes) > 0:
                prevVotesInt = 0
                for vote in previousVotes:
                    vote_amount = vote[3][:-1].split(";")
                    for x in vote_amount:
                        prevVotesInt += int(x)
                if prevVotesInt == maxvoteint:
                    await voteErrorHandler(
                        message, dm_channel, 8, poll_name=poll[0][5]
                    )  # user has already voted maximum amount
                    return
                else:
                    maxvoteint = prevVotesInt
            optionsCount = len(poll[0][4].split(";"))
            votes = []
            totalVotes = 0
            for i in range(optionsCount - 1):
                votes.append(0)
            for arg in args:
                if arg.strip() == "":
                    continue
                options = arg.split(":")
                try:
                    option_no = int(options[0].strip().lstrip("[").rstrip("]"))
                    vote_amount = int(options[1].strip().lstrip("[").rstrip("]"))
                except Exception:
                    await voteErrorHandler(message, dm_channel, 6)
                    return
                if option_no == 0 or option_no < 0:
                    await voteErrorHandler(message, dm_channel, 6)
                    return
                elif option_no > optionsCount:
                    await voteErrorHandler(message, dm_channel, 6)
                    return
                votes[option_no - 1] = vote_amount
                totalVotes += vote_amount

            if totalVotes > maxvoteint:
                await voteErrorHandler(message, dm_channel, 5, maxvotes=maxvoteint)
                return
            vote_str = ""
            for vote in votes:
                vote_str += f"{vote};"

            remainingVotes = maxvoteint - totalVotes
            c.execute("SELECT Vote_ID FROM RolePolls_Votes ORDER BY Vote_ID DESC")
            maxid = c.fetchone()
            if maxid == None:
                maxid = 1
            else:
                maxid = maxid[0]
            i = 0
            success = 0
            while i < 5:
                try:
                    c.execute(
                        "INSERT INTO RolePolls_Votes VALUES (?,?,?,?)",
                        (maxid + 1, poll_id, message.author.id, vote_str),
                    )
                    success = 1
                    break
                except sqlite3.IntegrityError:
                    maxid += 1
                    i += 1
                    continue
            if success != 1:
                await voteErrorHandler(
                    message, dm_channel, 7
                )  # unable to record the vote to database
                logging.error(
                    "Sqlite IntegrityError during voting. Vote recording was not succesful after 5 attempts."
                )
                return
            conn.commit()
            pollOptions = poll[0][4][:-1].split(";")
            txt = ""
            i = 0
            for v in votes:
                txt += f"**{pollOptions[i]}**: {v}\n"
                i += 1
            emb.description = txt
            emb.title = f"Your votes for '{poll[0][5]}' were:"
            emb.set_footer(
                text=f"You have {remainingVotes} votes left in this poll.\n\
                    If these are incorrect, you can use '!c vote delete {poll_id}' to delete your vote(s) and try again."
            )
            emb.color = get_hex_colour(cora_eye=True)
            await dm_channel.send(embed=emb)
            await message.delete()


async def voteErrorHandler(message, dm_channel, err_type, poll_name="", maxvotes=0):
    emb = discord.Embed()
    if err_type == 1:
        emb.description = f"\N{no entry} **Invalid poll ID. Please give the ID as an integer.**\
            Your command was: ```{message.content}```"
    elif err_type == 2:
        emb.description = f"\N{no entry} **No poll found with given poll ID on '{message.guild.name}'**\
            Your command was: ```{message.content}```"
    elif err_type == 3:
        emb.description = f"\N{no entry} **You do not have a role that can vote in the poll '{poll_name}' in '{message.guild.name}'**"
    elif err_type == 4:
        emb.description = f"\N{no entry} **You cannot vote in the poll with ID '{poll_name}' in '{message.guild.name}'**"
    elif err_type == 5:
        emb.description = f"\N{no entry} **You gave too many votes for poll '{poll_name}'. You can still give a maximum of {maxvotes}.\n\
            Your command was:** ```{message.content}```"
    elif err_type == 6:
        emb.description = f"\N{no entry} **Invalid option number or vote amount. Please give them as an integer and make sure they are within the poll options.**"
    elif err_type == 7:
        emb.description = f"\N{no entry} **Unable to record the vote. Please try again.**\n\
            Your command was: ```{message.content}```"
    elif err_type == 8:
        emb.description = f"\N{no entry} **You have already given maximum amount of votes into the poll '{poll_name}'.**"
    else:
        emb.description = "Something went wrong in voting."

    emb.color = get_hex_colour(error=True)
    await dm_channel.send(embed=emb)
    await message.delete()


async def voteHelp(message):
    emb = discord.Embed()
    emb.color = get_hex_colour()
    emb.title = "Voting in polls"
    emb.description = "You can vote in the _basic polls_ by reacting to the corresponding emote.\n\
    The vote command can be used in _advanced polls_ (indicated by the poll having numbers before the options instead of emotes).\
    **Vote command usage:**\n\
    ```!c vote [Poll ID] [option number]:[amount of votes], [option number]:[amount of votes], ...```\n\
    _NOTE!_ Poll ID can be found in the footer under the poll. You do not need to type the brackets.\n\
    You also do not need to type the options that you are not voting for, only those you _are_ voting for.\n\
    \n\
    **Deleting your votes**\n\
    If your votes were incorrect or you want to change them, you can use \n\
    ```!c vote delete [Poll ID]```\n\
    to delete all your votes from that poll and try again."

    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()

    await dm_channel.send(embed=emb)
    await message.delete()


async def delVotes(message):
    # Command structure
    # !c vote delete [Poll ID]

    emb = discord.Embed()
    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()
    arg = message.content.split(" ")[3]
    try:
        poll_id = int(arg.strip().lstrip("[").rstrip("'").rstrip("]"))
    except ValueError:
        await voteErrorHandler(message, dm_channel, 1)  # invalid Poll ID
        return

    with sqlite3.connect(DB_F) as conn:
        c = conn.cursor()

        c.execute(
            "DELETE FROM RolePolls_Votes WHERE Poll_ID=? AND Voter_ID=?",
            (poll_id, message.author.id),
        )
        conn.commit()
        emb.title = f"Your votes were deleted from poll with ID {poll_id}"
        emb.color = get_hex_colour(cora_eye=True)
        await dm_channel.send(embed=emb)
        await message.delete()
