# CoraBot
# Copyright 2021 (c) Appelsiini1

import discord
import logging
from datetime import datetime
from discord.ext import commands
import traceback

# scripts, functions & constants5
from constants import *
from modules import command_help
from modules import common
from modules import quote
from modules import insult
from modules import choose
from modules import giveaway
from modules import pressF
from modules import vaccine
from modules import tirsk
from modules import poll
from modules import vote
from modules import pop
from modules import nitro
from modules import dice_comm
#from modules import auction
from modules import short_comms
from modules import saimaa
from modules import message_listener
from modules import mood

# Main bot class
class CoraBot(commands.Bot):
    def __init__(self):
        command_prefix = PREFIX
        super().__init__(
            command_prefix, help_command=None, intents=INTENTS, activity=ACTIVITY
        )
        self.remove_command("help")
        self.__cogsetup__()
        self.run(DISCORD_TOKEN)

    def __cogsetup__(self):
        # Load cogs
        #auction.setup(self)
        command_help.setup(self)
        choose.setup(self)
        dice_comm.setup(self)
        giveaway.setup(self)
        short_comms.setup(self)
        insult.setup(self)
        message_listener.setup(self)
        mood.setup(self)
        nitro.setup(self)
        poll.setup(self)
        pop.setup(self)
        pressF.setup(self)
        quote.setup(self)
        saimaa.setup(self)
        tirsk.setup(self)
        vaccine.setup(self)
        vote.setup(self)

    async def on_ready(self):
        print(f"{self.user.name} {VERSION} is online & ready.")
        logging.info(f"{self.user.name} {VERSION} is online & ready.")

    async def on_command_error(self, ctx, error):
        print("Error!")
        logging.error("Command Error!")
        time = datetime.now().strftime("%d.%m.%Y at %H:%M")
        ignored = (
            commands.NoPrivateMessage,
            commands.DisabledCommand,
            commands.CheckFailure,
            commands.UserInputError,
            discord.HTTPException,
        )
        error = getattr(error, "original", error)

        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.CommandNotFound):
            await ctx.send("What was that?")
            return

        exc = traceback.format_exception(
            type(error), error, error.__traceback__, chain=False
        )
        description = "\n%s\n" % "".join(exc)

        name = ctx.command.qualified_name
        author = f"{ctx.message.author} (ID: {ctx.message.author.id})"
        try:
            location = f"{ctx.message.channel}/{ctx.message.server}"
        except AttributeError:
            location = "MAIN"

        message = f"{name} at {time}: Called by: {author} in {location}. More info: {description}"
        print(
            f"{time} - An unhandled exception occured in {location}, see log for details."
        )

        logging.error(message)

    async def on_guild_join(guild):
        emb = discord.Embed()
        emb.color = common.get_hex_colour(cora_blonde=True)
        emb.title = "Hey there!"
        emb.description = "Hi! Thanks for adding me to your server! <3\n\
            You can use my features by typing commands with the prefix `!c`. To access a list of available commands, use `!c help`.\n\
            \nPlease make sure I have the proper rights, especially to view the channels you want me to listen for commands in, send messages & embed links.\n\
            \n\
            Sincerely,\n\
            ~ Cora ~"
        emb.set_thumbnail(
            url="https://media.discordapp.net/attachments/693166291468681227/834200862246043648/cora_pfp.png"
        )
        try:
            dm_channel = guild.owner.dm_channel
            if dm_channel == None:
                dm_channel = await guild.owner.create_dm()
            await dm_channel.send(embed=emb)
        except Exception:
            logging.exception("Could not send welcome message to server owner.")

    async def on_error(event, *args, **kwargs):
        time = datetime.now().strftime("%d.%m.%Y at %H:%M")
        logging.exception(
            f"An unhandled exception occured in {event}. \nMessage: {args[0]}'\n**********"
        )
        print(
            f"{time} - An unhandled exception occured in {event}, see log for details."
        )


def main():
    logging.basicConfig(
        filename="Coralog.txt",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    common.initializeDatabase()
    CLIENT = CoraBot()


if __name__ == "__main__":
    main()
