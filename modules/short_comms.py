from discord import Embed, File
from discord.errors import Forbidden
from discord.ext import commands
from modules.common import forbiddenErrorHandler, get_hex_colour, check_if_channel, check_if_bot
import subprocess


class Short(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["hello"])
    @commands.check(check_if_channel)
    @commands.check(check_if_bot)
    async def hi(self, ctx):
        if ctx.invoked_with == "hi":
            try:
                await ctx.send("Hello!")
            except Forbidden:
                await forbiddenErrorHandler(ctx.message)
        else:
            try:
                await ctx.send("Hi!")
            except Forbidden:
                await forbiddenErrorHandler(ctx.message)

    @commands.command()
    @commands.check(check_if_channel)
    @commands.check(check_if_bot)
    async def status(self, ctx):
        emb = Embed()
        emb.color = get_hex_colour()
        emb.title = "CoraBot Status:"
        emb.description = "**418** I'm a teapot"
        try:
            await ctx.send(embed=emb)
        except Forbidden:
            await forbiddenErrorHandler(ctx.message)

    @commands.command()
    async def save(self, ctx):
        """
        Runs a command using subprocess and captures output.
        Returns an instance of CompletedProcess if runs is a success.
        On error returns an instance of CalledProcessError, TimeoutExpired,
        or FileNotFoundError.

        Params:
        command: the command to run as string
        inputs: the inputs that are given to the command or None
        process_timeout: Defaults to 10 (seconds).
        """

        try:
            output = subprocess.run(
                "tar -cvf archive.tar /CoraBot && mv ~/archive.tar ~/CoraBot",
                cwd="~/",
                capture_output=True,
                text=True,
                check=True,
            )
            # capture_output saves stdout ja stderr during the run
            # Text changes bytes to str
            # check raises CalledProcessError if exit code is not 0
            # timeout stops the process if it takes longer than given value

        except Exception:
            print("Process exited with non-zero code.")
        else:
            print(output)

        fileToSend = File("archive.tar")
        dm_channel = ctx.author.dm_channel
        if dm_channel == None:
            dm_channel = await ctx.author.create_dm()
        await dm_channel.send(file=fileToSend)
        emb = Embed()
        emb.title = ""
        emb.description = (
            "**Bot data succesfully compiled and sent to you.**"
        )
        emb.color = get_hex_colour(cora_eye=True)
        await dm_channel.send(embed=emb)

    # @commands.command()
    # @commands.check(check_if_channel)
    # @commands.check(check_if_bot)
    # async def mood(self, ctx):
    #     try:
    #         await ctx.send(
    #             "https://cdn.discordapp.com/attachments/816694548457324544/830847194142605403/hui_saakeli_tata_elamaa.mp4"
    #         )
    #     except Forbidden:
    #         await forbiddenErrorHandler(ctx.message)


def setup(client):
    client.add_cog(Short(client))