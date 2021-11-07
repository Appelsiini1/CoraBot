import discord
import sqlite3
import logging
import datetime
from discord.ext import commands
from modules.common import forbiddenErrorHandler, get_hex_colour, check_if_bot, check_if_channel
from modules.command_help import voteHelp
from constants import DB_F


class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(check_if_channel)
    @commands.check(check_if_bot)
    async def vote(self, ctx):
        # Command structure
        # !c vote [Poll ID] [option number]:[amount of votes], [option number]:[amount of votes], ...

        try:
            arg = ctx.message.content.split(" ")[2]
        except IndexError:
            arg = ""

        dm_channel = ctx.author.dm_channel
        if dm_channel == None:
            dm_channel = await ctx.author.create_dm()
        emb = discord.Embed()

        if arg == "":
            await voteHelp(ctx.message)
        elif arg.strip() == "help":
            await voteHelp(ctx.message)
        elif arg.strip() == "delete":
            await self.delVotes(ctx.message)
        else:
            try:
                poll_id = int(arg.strip().lstrip("[").rstrip("]"))
            except ValueError:
                await self.voteErrorHandler(
                    ctx.message, dm_channel, 1
                )  # invalid Poll ID
                return

            with sqlite3.connect(DB_F) as conn:
                prefix = "!c vote " + arg
                args = ctx.message.content[len(prefix) :].split(",")
                c = conn.cursor()

                c.execute(
                    "SELECT * FROM RolePolls WHERE Poll_ID=? AND Guild_ID=?",
                    (poll_id, ctx.guild.id),
                )
                poll = c.fetchall()
                if len(poll) == 0:
                    await self.voteErrorHandler(
                        ctx.message, dm_channel, 2
                    )  # no poll exists with poll ID
                    return
                else:
                    c.execute(
                        f"SELECT * FROM RolesMaxVotes WHERE Guild_ID={ctx.guild.id}"
                    )
                    VoteRoles = c.fetchall()
                    MemberRoles = ctx.author.roles

                    roleIDList = []
                    foundRoles = []
                    for r in MemberRoles:
                        roleIDList.append(r.id)

                    for role in VoteRoles:
                        if role[0] in roleIDList:
                            foundRoles.append(role)
                    if len(foundRoles) == 0:
                        await self.voteErrorHandler(
                            ctx.message, dm_channel, 3, poll_name=poll[0][5]
                        )  # user does not have roles that can vote
                        return
                    else:
                        maxvoteint = 0
                        for role in foundRoles:
                            if role[3] > maxvoteint:
                                maxvoteint = role[3]
                        if maxvoteint == 0:
                            await self.voteErrorHandler(
                                ctx.message, dm_channel, 8, poll_name=poll[0][5]
                            )  # user has zero votes
                            return
                c.execute(
                    "SELECT * FROM RolePolls_Votes WHERE Voter_ID=? AND Poll_ID=?",
                    (ctx.author.id, poll_id),
                )
                previousVotes = c.fetchall()
                if len(previousVotes) > 0:
                    prevVotesInt = 0
                    for vote in previousVotes:
                        vote_amount = vote[3][:-1].split(";")
                        for x in vote_amount:
                            prevVotesInt += int(x)
                    if prevVotesInt == maxvoteint:
                        await self.voteErrorHandler(
                            ctx.message, dm_channel, 8, poll_name=poll[0][5]
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
                        await self.voteErrorHandler(
                            ctx.message, dm_channel, 6, poll_name=poll[0][5]
                        )
                        return
                    if option_no == 0 or option_no < 0:
                        await self.voteErrorHandler(
                            ctx.message, dm_channel, 6, poll_name=poll[0][5]
                        )
                        return
                    elif option_no > optionsCount:
                        await self.voteErrorHandler(
                            ctx.message, dm_channel, 6, poll_name=poll[0][5]
                        )
                        return
                    elif vote_amount < 0:
                        await self.voteErrorHandler(
                            ctx.message, dm_channel, 6, poll_name=poll[0][5]
                        )
                    try:
                        votes[option_no - 1] = vote_amount
                    except IndexError:
                        await self.voteErrorHandler(
                            ctx.message, dm_channel, 6, poll_name=poll[0][5]
                        )
                        logging.error(
                            f"Unknown exception handled in '!c vote'. The command was: {ctx.message.content}"
                        )
                    totalVotes += vote_amount

                if totalVotes > maxvoteint:
                    await self.voteErrorHandler(
                        ctx.message,
                        dm_channel,
                        5,
                        maxvotes=maxvoteint,
                        poll_name=poll[0][5],
                    )
                    return
                vote_str = ""
                for vote in votes:
                    vote_str += f"{vote};"

                remainingVotes = maxvoteint - totalVotes
                timestamp = datetime.datetime.today().strftime("%d.%m.%Y %H:%M %Z%z")

                c.execute(
                    "INSERT INTO RolePolls_Votes VALUES (?,?,?,?,?)",
                    (None, poll_id, ctx.author.id, vote_str, timestamp),
                )

                conn.commit()
                pollOptions = poll[0][4][:-1].split(";")
                txt = ""
                for i, v in enumerate(votes):
                    txt += f"**{pollOptions[i]}**: {v}\n"
                emb.description = txt
                emb.title = f"Your votes for '{poll[0][5]}' were:"
                emb.set_footer(
                    text=f"You have {remainingVotes} votes left in this poll.\nIf your votes look incorrect, you can use `!c vote delete {poll_id}` to delete your vote(s) and try again."
                )
                emb.color = get_hex_colour(cora_eye=True)
                try:
                    await dm_channel.send(embed=emb)
                except discord.Forbidden:
                    self.voteErrorHandler(ctx.message, dm_channel, 9, poll_name=poll[0][5])
                await ctx.message.delete()

    async def voteErrorHandler(
        self, message, dm_channel, err_type, poll_name="", maxvotes=0
    ):
        emb = discord.Embed()
        if err_type == 1:
            emb.description = f"\N{no entry} **Invalid poll ID. Please give the ID as an integer. See `!c vote help` for more help.**\
                \nYour command was: ```{message.content}```"
        elif err_type == 2:
            emb.description = f"\N{no entry} **No poll found with given poll ID on '{message.guild.name}'**\
                \nYour command was: ```{message.content}```"
        elif err_type == 3:
            emb.description = f"\N{no entry} **You do not have a role that can vote in the poll '{poll_name}' in '{message.guild.name}'**"

        elif err_type == 4:  # depricated, use err_type 8 instead.
            emb.description = f"\N{no entry} **You cannot vote in the poll with ID '{poll_name}' in '{message.guild.name}'**"

        elif err_type == 5:
            emb.description = f"\N{no entry} **You gave too many votes for poll '{poll_name}'. You can still give a maximum of {maxvotes}.**\n\
                Your command was: ```{message.content}```"
        elif err_type == 6:
            emb.description = f"\N{no entry} **Invalid option number or vote amount in poll {poll_name}. Please give them as an integer and make sure they are within the poll options.\n\
                See `!c vote help` for more help.**\n\
                Your command was: ```{message.content}```"
        elif err_type == 7:
            emb.description = f"\N{no entry} **Unable to record the vote due to a database error. Please try again.**\n\
                Your command was: ```{message.content}```"
        elif err_type == 8:
            emb.description = f"\N{no entry} **You have already given maximum amount of votes into the poll '{poll_name}'.**"
        elif err_type == 9:
            emb.description = f"\N{no entry} **{message.author.mention} Your votes were succesfully registered to the poll '{poll_name}', but I was unable to send a confirmation via a private message. Please check that you have private messages enabled on the server if you wish to get confirmations in the future.**"
            emb.color = get_hex_colour(error=True)
            try:
                await message.channel.send(embed=emb)
            except discord.Forbidden:
                forbiddenErrorHandler(message)
            try:
                await message.delete()
            except discord.errors.NotFound:
                logging.exception(
                    "Could not delete vote command message. Message not found."
                )
            return
        else:
            emb.description = "Something went wrong in voting."

        emb.color = get_hex_colour(error=True)
        try:
            await dm_channel.send(embed=emb)
        except discord.Forbidden:
            emb.description = f"\N{no entry} **{message.author.mention} There was an error in your vote command and I was unable to send you details via a private message. Please enable private messages for this server and try again.**"
            try:
                await message.channel.send(embed=emb)
            except discord.Forbidden:
                forbiddenErrorHandler(message)
        try:
            await message.delete()
        except discord.errors.NotFound:
            logging.exception(
                "Could not delete vote command message. Message not found."
            )

    async def delVotes(self, message):
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
            await self.voteErrorHandler(message, dm_channel, 1)  # invalid Poll ID
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


def setup(client):
    client.add_cog(Vote(client))