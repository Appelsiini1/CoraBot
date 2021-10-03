import discord
import logging
import datetime
import sqlite3
from currency_symbols import CurrencySymbols
from dateutil import tz
from discord.ext import commands
from modules.common import (
    get_hex_colour,
    forbiddenErrorHandler,
    timeParser,
    timeConverter,
)
from constants import DB_F, TRACKED_CHANNELS
from modules.command_help import auction_help
from modules.scheduler import addEvent


async def bid(message):
    pass


class AUCTION_INFO:
    def __init__(
        self,
        title,
        slots,
        currency_symbol,
        start_bid,
        min_inc,
        autobuy,
        start_time,
        end_time,
        start_time_raw,
        end_time_raw,
        startsNow,
        timezone,
    ):
        self.title = title
        self.slots = slots
        self.currency = currency_symbol
        self.startBid = start_bid
        self.minInc = min_inc
        self.autobuy = autobuy
        self.startTime = start_time
        self.endTime = end_time
        self.startsNow = startsNow
        self.rawStartTime = start_time_raw
        self.rawEndTime = end_time_raw
        self.timezone = timezone


class AUCTION(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # helper function
    async def sendEmbed(self, ctx, emb):
        try:
            await ctx.send(embed=emb)
            return
        except discord.errors.Forbidden:
            await forbiddenErrorHandler(ctx.message)
            return

    # parse auction start
    async def parseStartCommand(self, ctx):
        cmd_split = ctx.message.content.split(" ")
        emb = discord.Embed()

        if len(cmd_split) <= 3:
            emb.title = "No arguments given, see `!c auction help` for correct syntax."
            emb.color = get_hex_colour(error=True)

            await self.sendEmbed(ctx, emb)
            return -1

        elif len(cmd_split[3].split(";")) < 8:
            emb.title = "Too few arguments. Please remember to give all arguments. See `!c auction help` for more information."
            emb.color = get_hex_colour(error=True)

            await self.sendEmbed(ctx, emb)
            return -1
        else:
            args = cmd_split[3].split(";")
            title = args[0].strip()
            slots = args[1].strip().lstrip("[").rstrip("]")
            currency = args[2].strip().lstrip("[").rstrip("]").upper()
            start_bid = args[2].strip().lstrip("[").rstrip("]")
            min_inc = args[3].strip().lstrip("[").rstrip("]")
            autobuy = args[4].strip().lstrip("[").rstrip("]")
            start_time_raw = args[5].strip().lstrip("[").rstrip("]").lower()
            end_time_raw = args[6].strip().lstrip("[").rstrip("]").lower()

            try:
                start_bid = int(start_bid)
                min_inc = int(min_inc)
                autobuy = int(autobuy)
                slots = int(slots)
            except ValueError:
                emb.title = "Number of slots, starting bid, minimum increase or autobuy value(s) are not integers."
                emb.color = get_hex_colour(error=True)

                await self.sendEmbed(ctx, emb)
                return -1

            if start_bid == 0:
                emb.title = "Starting bid must be greater than zero."
                emb.color = get_hex_colour(error=True)

                await self.sendEmbed(ctx, emb)
                return -1

            currency_symbol = CurrencySymbols.get_symbol(currency)
            if currency_symbol == None:
                emb.title = "Unknown currency code."
                emb.color = get_hex_colour(error=True)
                await self.sendEmbed(ctx, emb)
                return -1

            if start_time_raw == "now":
                timezone = tz.gettz()
                start_time = datetime.datetime.today().replace(tzinfo=timezone)
                startsnow = 1
            else:
                try:
                    start_time = timeParser(start_time_raw)
                    startsnow = 0
                    timezone = (
                        start_time_raw.split(",")[1].strip().lstrip("[").rstrip("]")
                    )
                except ValueError:
                    emb.title = "Error parsing start time, does not match the time format `dd.mm.yyyy HH:MM, Area/Location` or timezone not recognized."
                    emb.color = get_hex_colour(error=True)
                    await self.sendEmbed(ctx, emb)
                    return -1

            if end_time_raw != "":
                try:
                    end_time = timeParser(end_time_raw)
                except ValueError:
                    emb.title = "Error parsing end time, does not match the time format `dd.mm.yyyy HH:MM, TIMEZONE` or timezone not recognized."
                    emb.color = get_hex_colour(error=True)
                    await self.sendEmbed(ctx, emb)
                    return -1
            else:
                end_time = None

            auctionInfo = AUCTION_INFO(
                title,
                slots,
                currency_symbol,
                start_bid,
                min_inc,
                autobuy,
                start_time,
                end_time,
                start_time_raw,
                end_time_raw,
                startsnow,
                timezone,
            )
            return auctionInfo

    # add auction to schedule and construct info message
    async def makeAuction(self, ctx):
        # Command structure
        # !c auction start title;number of slots [int];currency as a 3-letter identifier (ISO-4217);starting bid [int, x > 0];min increase [int, x >= 0];autobuy [int, 0 if disabled, x >= 0];start time [DD.MM.YYYY HH:MM, Area/Location (as 24-hour clock)(Timezone as per the Olson database)] or [now];end time or empty
        # Countdown example: https://www.timeanddate.com/countdown/generic?iso=20240322T1442&p0=101&msg=Event+name&font=cursive&csz=1 NOTES: Always Helsinki time (p0=101), csz=1 -> stop countdown at zero

        parsed = self.parseStartCommand(ctx)
        if parsed == -1:
            return

        # Auction_ID INT,   0
        # Channel_ID INT,   1
        # Guild_ID INT,     2
        # Author_ID INT,    3
        # Slots TEXT,       4
        # Currency TEXT,    5
        # Starting_bid INT, 6
        # Min_increase INT, 7
        # Autobuy INT,      8
        # Start_time TEXT,  9
        # End_time TEXT,    10
        # PRIMARY KEY (Auction_ID)
        with sqlite3.connect(DB_F) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO Tracked VALUES (?,?,?)",
                (ctx.channel.id, ctx.guild.id, 2),
            )

            c.execute(
                "INSERT INTO Auctions VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    None,
                    ctx.channel.id,
                    ctx.guild.id,
                    ctx.author.id,
                    parsed.slots,
                    parsed.currency,
                    parsed.startBid,
                    parsed.minInc,
                    parsed.autobuy,
                    parsed.rawStartTime,
                    parsed.rawEndTime,
                ),
            )
            conn.commit()
            c.execute(
                f"SELECT Auction_ID FROM Auctions WHERE Channel_ID={ctx.channel.id} AND Author_ID={ctx.author.id}"
            )
            auctionID = c.fetchone()[0]
            if parsed.startsnow == 1:
                self.startAuction()
            else:
                addEvent(
                    1,
                    parsed.rawStartTime,
                    parsed.title,
                    auctionID,
                    parsed.timezone,
                )
                if parsed.end_time != None:
                    addEvent(
                        2, parsed.rawEndtime, parsed.title, auctionID, parsed.timezone
                    )

    async def startAuction(self):
        pass

    async def endAuction(self, ctx):
        pass

    @commands.command(name="auction")
    async def auctionJunction(self, ctx):
        try:
            cmd = (
                ctx.message.content.split(" ")[2]
                .strip()
                .lstrip("[")
                .rstrip("]")
                .lower()
            )
        except IndexError:
            emb = discord.Embed()
            emb.title = "No argument given. See `!c auction help` for arguments."
            emb.color = get_hex_colour(error=True)

            try:
                await ctx.send(embed=emb)
                return
            except discord.errors.Forbidden:
                await forbiddenErrorHandler(ctx.message)
                return

        if cmd == "start":
            await self.makeAuction(ctx)
        elif cmd == "stop":
            await self.endAuction(ctx)
        elif cmd == "help":
            await auction_help()
        else:
            emb = discord.Embed()
            emb.title = "Invalid argument. See `!c auction help` for correct syntax."
            emb.color = get_hex_colour(error=True)

            try:
                await ctx.send(embed=emb)
            except discord.errors.Forbidden:
                await forbiddenErrorHandler(ctx.message)


def setup(client):
    client.add_cog(AUCTION(client))


async def testFunction():
    print("working...")
    # channel = await .fetch_channel(822224994788180019)
    # await channel.send("hello!")
