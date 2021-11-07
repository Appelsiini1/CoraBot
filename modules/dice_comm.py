import dice
import discord
import logging
import os

from discord.ext import commands

from modules.common import get_hex_colour, forbiddenErrorHandler, check_if_channel, check_if_bot
from modules.command_help import dice_help

MAX_DICE = 2 ** 20


class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dice")
    @commands.check(check_if_channel)
    @commands.check(check_if_bot)
    async def dice_comm(self, ctx):
        # Command structure
        # !c dice [help | [N]dS]
        try:
            arg = (
                ctx.message.content.split(" ")[2]
                .strip()
                .lstrip("[")
                .rstrip("]")
                .lower()
            )
        except IndexError:
            await ctx.send("No arguments given. Valid arguments are `help` and `[N]dS`")
            return

        if arg == "help":
            await dice_help(ctx)
            return
        else:
            emb = discord.Embed()
            if arg.startswith("d") or arg.startswith("w") or arg.startswith("u"):
                pass
            else:
                try:
                    dices = arg.split("d")
                    if len(dices) == 1:
                        dices = arg.split("w")
                        if len(dices) == 1:
                            dices = arg.split("u")
                            if len(dices) == 1:
                                emb.title = "Unknown dice mode. Valid modes are `d`, `u` and `w`."
                                emb.color = get_hex_colour(error=True)
                                try:
                                    await ctx.send(embed=emb)
                                except discord.errors.Forbidden:
                                    await forbiddenErrorHandler(ctx.message)
                            else:
                                if int(dices[0]) > MAX_DICE:
                                    emb.title = "Too many dice!"
                                    emb.color = get_hex_colour(error=True)
                                    try:
                                        await ctx.send(embed=emb)
                                    except discord.errors.Forbidden:
                                        await forbiddenErrorHandler(ctx.message)
                                    return
                        else:
                            if int(dices[0]) > MAX_DICE:
                                emb.title = "Too many dice!"
                                emb.color = get_hex_colour(error=True)
                                try:
                                    await ctx.send(embed=emb)
                                except discord.errors.Forbidden:
                                    await forbiddenErrorHandler(ctx.message)
                                return
                    else:
                        if int(dices[0]) > MAX_DICE:
                            emb.title = "Too many dice!"
                            emb.color = get_hex_colour(error=True)
                            try:
                                await ctx.send(embed=emb)
                            except discord.errors.Forbidden:
                                await forbiddenErrorHandler(ctx.message)
                            return
                except Exception:
                    logging.exception("Error parsing dice.")
                    emb.title = "Error parsing dice. Please check arguments."
                    emb.color = get_hex_colour(error=True)
                    try:
                        await ctx.send(embed=emb)
                    except discord.errors.Forbidden:
                        await forbiddenErrorHandler(ctx.message)
                    return
                if int(dices[0]) > 20000:
                    await ctx.channel.trigger_typing()

            try:
                result = dice.roll(arg)
            except Exception:
                logging.exception("Error throwing dice.")
                emb.title = "Error throwing dice. Please check arguments."
                emb.color = get_hex_colour(error=True)
                try:
                    await ctx.send(embed=emb)
                except discord.errors.Forbidden:
                    await forbiddenErrorHandler(ctx)
                return

            try:
                res_len = len(result)
            except TypeError:
                res_len = -1
            if type(result) == dice.elements.Roll:
                dice_mode = "normal dice roll"
            elif type(result) == dice.elements.WildRoll:
                dice_mode = "wild dice roll"
            elif type(result) == dice.elements.ExplodedRoll:
                dice_mode = "exploded dice roll"
            else:
                dice_mode = "dice roll"

            dice_string = ""

            if res_len == -1:
                dice_string = f"{result}"
            else:
                for i in result:
                    dice_string += f"{i}, "
                dice_string = dice_string[:-2]
                if len(dice_string) > 2048:
                    filename = "results.txt"
                    try:
                        with open(filename, "w", encoding="utf-8") as f:
                            i = 0
                            for r in result:
                                if i == 15:
                                    f.write("\n")
                                    i = 0
                                else:
                                    f.write(f"{r}, ")
                                    i += 1
                    except Exception:
                        logging.exception("Error writing dice result file")
                    fileToSend = discord.File(filename)
                    try:
                        await ctx.send(f"**Your {dice_mode} result:**")
                        await ctx.send(file=fileToSend)
                    except discord.errors.Forbidden:
                        await forbiddenErrorHandler(ctx)
                    finally:
                        try:
                            os.remove(filename)
                        except Exception:
                            logging.exception(
                                "Unable to delete the local copy of dice result."
                            )
            if len(dice_string) < 2048:
                emb.description = f"**Your {dice_mode} result:**\n```{dice_string}```"
                emb.color = get_hex_colour()
                try:
                    await ctx.send(embed=emb)
                except discord.errors.Forbidden:
                    await forbiddenErrorHandler(ctx)


def setup(client):
    client.add_cog(Dice(client))
