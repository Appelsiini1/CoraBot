import dice
import discord
import logging
import os

from discord.ext import commands

from modules.common import get_hex_colour, forbiddenErrorHandler

MAX_DICE = 2 ** 20

class Dice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def dice_help(self, ctx):
        txt = "_The following operators are listed in order of precedence. Parentheses may be used to force an alternate order of evaluation._\n\n\
            The dice (`[N]dS`) operator takes an amount (N) and a number of sides (S), and returns a list of N random numbers between 1 and S. For example: `4d6` may return `6, 3, 2, 4`. Usin a `%` as the second operand is shorthand for rolling a d100, and a using `f` is shorthand for ±1 fudge dice.\n\n\
            The fudge dice (`[N]uS`) operator is interchangable with the dice operator, but makes the dice’s range from -S to S instead of 1 to S. This includes 0.\n\n\
            A wild dice (`[N]wS`) roll is special. The last roll in this set is called the “wild die”. If this die’s roll is the maximum value, the second-highest roll in the set is set to the maximum value. If its roll is the minimum, then both it and the highest roll in the set aer set to zero. Then another die is rolled. If this roll is the minimum value again, then ALL die are set to zero. If a single-sided wild die is rolled, the roll behaves like a normal one.\n\n\
            If N is not specified, it is assumed you want to roll a single die. `d6` is equivalent to `1d6`.\n\n\
            Rolls can be exploded with the `x` operator, which adds an additional dice to the set for each roll above a given threshold. If a threshold isn’t given, it defaults to the maximum possible roll. If the extra dice exceed this threshold, they “explode” again! Safeguards are in place to prevent this from crashing the parser with infinite explosions. Example: `2d6x2` could return `5, 4, 1, 5, 2, 6, 1`.\
            "
        txt2 = "The highest, middle or lowest rolls or list entries can be selected with (`^` or `h`), (`m` or `o`), or (`v` or `l`) respectively. `6d6^3` will keep the highest 3 rolls, whereas `6d6v3` will select the lowest 3 rolls. If a number isn’t specified, it defaults to keeping all but one for highest and lowest, and all but two for the middle. If a negative value is given as the operand for any of these operators, this operation will drop that many elements from the result. For example, `6d6^-2` will drop the two lowest values from the set, leaving the 4 highest. Zero has no effect.\n\n\
            A list or set of rolls can be turned into an integer with the total (`t`) operator. `6d1t` will return `6` instead of `1, 1, 1, 1, 1, 1`.\n\n\
            A set of dice rolls can be sorted with the sort (`s`) operator. `4d6s` will not change the return value, but the dice will be sorted from lowest to highest.\n\n\
            The `+-` operator is a special prefix for sets of rolls and lists. It negates odd roles within a list. Example: `1, 2, 3` -> `-1, 2, -3`. There is also a negate (`-`) operator, which works on either single elements, sets or rolls, or lists. There is also an identity `+` operator.\n\n\
            Values can be added or subtracted from each element of a list or set of rolls with the pointwise add (`.+`) and subtract (`.-`) operators. For example: `4d1 .+ 3` will return `4, 4, 4, 4`.\
            "
        emb = discord.Embed()
        emb.title = "Dice Help 1/2"
        emb.set_footer(text="Source: https://pypi.org/project/dice/")
        emb.color = get_hex_colour()
        dm_channel = ctx.author.dm_channel
        if dm_channel == None:
            dm_channel = await ctx.author.create_dm()

        emb.description = txt
        await dm_channel.send(embed=emb)
        emb.title = "Dice Help 2/2"
        emb.description = txt2
        await dm_channel.send(embed=emb)
        await ctx.send(
            "Help message for dice command has been sent via a private message."
        )

    @commands.command(name="dice")
    async def dice_comm(self, ctx):
        # Command structure
        # !c dice [help | [N]dS]
        try:
            arg = ctx.message.content.split(" ")[2].strip().lstrip("[").rstrip("]").lower()
        except IndexError:
            await ctx.send(
                "No arguments given. Valid arguments are `help` and `[N]dS`"
            )
            return

        if arg == "help":
            await self.dice_help(ctx)
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
                                emb.title = (
                                    "Unknown dice mode. Valid modes are `d`, `u` and `w`."
                                )
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
                    with open(filename, "w", encoding="utf-8") as f:
                        i = 0
                        for r in result:
                            if i == 15:
                                f.write("\n")
                                i = 0
                            else:
                                f.write(f"{r}, ")
                                i += 1
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
                                "Unable to delete the local copy of boost export CSV."
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
