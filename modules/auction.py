import discord
import logging
import datetime
import sqlite3
from currency_symbols import CurrencySymbols
from discord.ext import commands
from modules.common import get_hex_colour, forbiddenErrorHandler
from constants import DB_F, TRACKED_CHANNELS

# from modules.scheduler import


async def bid(message):
    pass


class Auction(commands.Cog):
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

    # add auction to schedule and construct info message
    async def makeAuction(self, ctx, scheduler):
        # Command structure
        # !c auction start title;number of slots [int];currency as a 3-letter identifier (ISO-4217);starting bid [int, x > 0];min increase [int, x >= 0];autobuy [int, 0 if disabled, x >= 0];start time [DD.MM.YYYY HH:MM UTC-/+HHMM (as 24-hour clock)] or [now];end time or empty
        # Countdown example: https://www.timeanddate.com/countdown/generic?iso=20240322T1442&p0=101&msg=Event+name&font=cursive&csz=1 NOTESa: Always Helsinki time (p0=101), csz=1 -> stop countdown at zero

        cmd_split = ctx.message.content.split(" ")
        emb = discord.Embed()

        if len(cmd_split) <= 3:
            emb.title = "No arguments given, see `!c auction help` for correct syntax."
            emb.color = get_hex_colour(error=True)

            await self.sendEmbed(ctx, emb)
            return
        elif len(cmd_split[3].split(";")) < 8:
            emb.title = "Too few arguments. Please remember to give all arguments. See `!c auction help` for more information."
            emb.color = get_hex_colour(error=True)

            await self.sendEmbed(ctx, emb)
            return
        else:
            args = cmd_split[3].split(";")
            title = args[0].strip()
            slots = args[1].strip().lstrip("[").rstrip("]")
            currency = args[2].strip().lstrip("[").rstrip("]").upper()
            start_bid = args[2].strip().lstrip("[").rstrip("]")
            min_inc = args[3].strip().lstrip("[").rstrip("]")
            autobuy = args[4].strip().lstrip("[").rstrip("]")
            start_time = args[5].strip().lstrip("[").rstrip("]").lower()
            end_time = args[6].strip().lstrip("[").rstrip("]").lower()

            try:
                start_bid = int(start_bid)
                min_inc = int(min_inc)
                autobuy = int(autobuy)
                slots = int(slots)
            except ValueError:
                emb.title = "Number of slots, starting bid, minimum increase or autobuy value(s) are not integers."
                emb.color = get_hex_colour(error=True)

                await self.sendEmbed(ctx, emb)
                return

            if start_bid == 0:
                emb.title = "Starting bid must be greater than zero."
                emb.color = get_hex_colour(error=True)

                await self.sendEmbed(ctx, emb)
                return

            currency_symbol = CurrencySymbols.get_symbol(currency)
            if currency_symbol == None:
                emb.title = "Unknown currency code."
                emb.color = get_hex_colour(error=True)
                await self.sendEmbed(ctx, emb)
                return

            if start_time == "now":
                start_time = datetime.datetime.today()
                startsnow = 1
            else:
                try:
                    start_time = datetime.datetime.strptime(
                        start_time, "%d.%m.%Y %H:%M %Z%z"
                    )
                    startsnow = 0
                except ValueError:
                    emb.title = "Error parsing start time, does not match the time format `dd.mm.yyyy HH:MM UTC±HHMM`."
                    emb.color = get_hex_colour(error=True)
                    await self.sendEmbed(ctx, emb)
                    return

            if end_time != "":
                try:
                    end_time = datetime.datetime.strptime(end_time, "%d.%m.%Y %H:%M")
                except ValueError:
                    emb.title = "Error parsing end time, does not match the time format `dd.mm.yyyy HH:MM UTC±HHMM`."
                    emb.color = get_hex_colour(error=True)
                    await self.sendEmbed(ctx, emb)
                    return

            # Auction_ID INT UNIQUE, 0
            # Channel_ID INT, 1
            # Guild_ID INT, 2
            # Author_ID INT, 3
            # Slots TEXT, 4
            # Currency TEXT, 5
            # Starting_bid INT, 6
            # Min_increase INT, 7
            # Autobuy INT, 8
            # Start_time TEXT, 9
            # End_time TEXT, 10
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
                        slots,
                        currency,
                        start_bid,
                        min_inc,
                        autobuy,
                        start_time,
                        end_time,
                    ),
                )
                conn.commit()

    async def startAuction(self):
        pass

    async def endAuction(self, ctx, scheduler):
        pass

    @commands.command(name="auction")
    async def auctionJunction(self, ctx, scheduler=None):
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
            await self.makeAuction(ctx, scheduler)
        elif cmd == "stop":
            await self.endAuction(ctx, scheduler)
        else:
            emb = discord.Embed()
            emb.title = "Invalid argument. See `!c auction help` for correct syntax."
            emb.color = get_hex_colour(error=True)

            try:
                await ctx.send(embed=emb)
            except discord.errors.Forbidden:
                await forbiddenErrorHandler(ctx.message)


def setup(client):
    client.add_cog(Auction(client))


async def testFunction():
    print("working...")
    # channel = await .fetch_channel(822224994788180019)
    # await channel.send("hello!")
