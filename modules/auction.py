import discord
import logging
import datetime

from modules.common import get_hex_colour, forbiddenErrorHandler
from constants import DB_F, TRACKED_CHANNELS


async def makeAuction(message):
    # Command structure
    # !c auction start title;starting bid [int, x > 0];min increase [int, x >= 0];autobuy [int, 0 if disabled, x >= 0];start time [DD.MM.YYYY HH:MM UTC-/+HHMM (as 24-hour clock)] or [now];end time or empty
    # Countdown example: https://www.timeanddate.com/countdown/generic?iso=20240322T1442&p0=101&msg=Event+name&font=cursive&csz=1 NOTE: Always Helsinki time

    cmd_split = message.content.split(" ")
    emb = discord.Embed()

    if len(cmd_split) <= 3:
        emb.title = "No arguments given, see `!c auction help` for correct syntax."
        emb.color = get_hex_colour(error=True)

        try:
            message.channel.send(embed=emb)
        except discord.errors.Forbidden:
            forbiddenErrorHandler(message)
            return
    elif len(cmd_split[3].split(";")) < 6:
        emb.title = "Too few arguments. Please remember to give all arguments. See `!c auction help` for more information."
        emb.color = get_hex_colour(error=True)

        try:
            message.channel.send(embed=emb)
        except discord.errors.Forbidden:
            forbiddenErrorHandler(message)
            return
    else:
        args = cmd_split[3].split(";")
        title = args[0].strip()
        start_bid = args[1].strip().lstrip("[").rstrip("]").lower()
        min_inc = args[2].strip().lstrip("[").rstrip("]").lower()
        autobuy = args[3].strip().lstrip("[").rstrip("]").lower()
        start_time = args[4].strip().lstrip("[").rstrip("]").lower()
        end_time = args[5].strip().lstrip("[").rstrip("]").lower()

        try:
            start_bid = int(start_bid)
            min_inc = int(min_inc)
            autobuy = int(autobuy)
        except ValueError:
            emb.title = (
                "Starting bid, minimum increase or autobuy value(s) are not integers."
            )
            emb.color = get_hex_colour(error=True)

            try:
                message.channel.send(embed=emb)
            except discord.errors.Forbidden:
                forbiddenErrorHandler(message)
                return

        if start_time == "now":
            start_time = datetime.datetime.today()
        else:
            try:
                start_time = datetime.datetime.strptime(
                    start_time, "%d.%m.%Y %H:%M %Z%z"
                )
            except ValueError:
                emb.title = "Error parsing start time, does not match the time format `dd.mm.yyyy HH:MM UTC±HHMM`."
                emb.color = get_hex_colour(error=True)
                try:
                    message.channel.send(embed=emb)
                except discord.errors.Forbidden:
                    forbiddenErrorHandler(message)
                    return

        if end_time != "":
            try:
                end_time = datetime.datetime.strptime(end_time, "%d.%m.%Y %H:%M")
            except ValueError:
                emb.title = "Error parsing end time, does not match the time format `dd.mm.yyyy HH:MM UTC±HHMM`."
                emb.color = get_hex_colour(error=True)
                try:
                    message.channel.send(embed=emb)
                except discord.errors.Forbidden:
                    forbiddenErrorHandler(message)
                    return


async def bid(message):
    pass


async def endAuction(message):
    pass


async def auctionJunction(message):
    try:
        cmd = message.content.split(" ")[2].strip().lstrip("[").rstrip("]").lower()
    except IndexError:
        emb = discord.Embed()
        emb.title = "No argument given. See `!c auction help` for arguments."
        emb.color = get_hex_colour(error=True)

        try:
            message.channel.send(embed=emb)
            return
        except discord.errors.Forbidden:
            await forbiddenErrorHandler(message)
            return

    if cmd == "start":
        await makeAuction(message)
    elif cmd == "stop":
        await endAuction(message)
    else:
        emb = discord.Embed()
        emb.title = "Invalid argument. See `!c auction help` for correct syntax."
        emb.color = get_hex_colour(error=True)

        try:
            message.channel.send(embed=emb)
        except discord.errors.Forbidden:
            forbiddenErrorHandler(message)
