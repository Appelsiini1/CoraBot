import logging
from discord.errors import Forbidden
from discord.ext import commands
from discord.errors import Forbidden
from discord import Embed
from modules.common import get_hex_colour, forbiddenErrorHandler
from constants import VERSION


class COMMAND_HELP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):
        cmd_list = """`hi` (alias: `hello`)
`help`
`info`
`inspire`
`insult [user]`
`f` (alias: `F`)
`choose option1 | option2 | ... `
`vacc [Area code (or empty for all areas) | help]`
`poll [new | end | help]`
`vote help`
`vote [Poll ID] [option:votes], [option:votes], ...`
`pop [number between 1-14]`
`dice [help | [N]dS | [N]wS | [N]uS]` (extra arguments can be seen from dice help)
`saimaa`

**_Admin commands:_**
`giveaway`
`endgiveaway [GiveawayID]`
`poll [set|del]roles`
`poll roles`
`poll new -r`
`nitro [help | add | del | export | start | stop | notice | check | spin | list]`
    """
        emb = Embed(
            title="List of available commands:",
            description=cmd_list,
            colour=get_hex_colour(cora_blonde=True),
        )
        try:
            await ctx.send(embed=emb)
        except Forbidden:
            logging.error("Unable to send message due to 403 - Forbidden")
            emb.clear_fields()
            emb.description = f"Unable to send message to channel in '{ctx.guild.name}'. If you are the server owner, please make sure I have the proper rights to post messages to that channel."
            emb.color = get_hex_colour(error=True)
            dm_channel = ctx.guild.owner.dm_channel
            if dm_channel == None:
                dm_channel = await ctx.guild.owner.create_dm()
            await dm_channel.send(embed=emb)

    @commands.command()
    async def info(self, ctx, *arg):
        emb = Embed()
        emb.title = "CoraBot Info"
        emb.description = f"**Created by** Appelsiini1\nThe source code & development info for this bot can be found at https://github.com/Appelsiini1/CoraBot\n\nVersion: {VERSION}"
        emb.color = get_hex_colour(cora_blonde=True)
        emb.set_thumbnail(
            url="https://media.discordapp.net/attachments/693166291468681227/834200862246043648/cora_pfp.png"
        )

        try:
            await ctx.send(embed=emb)
        except Forbidden:
            await forbiddenErrorHandler(ctx)


def setup(client):
    client.add_cog(COMMAND_HELP(client))


async def auction_help():
    pass

async def pollHelp(message):
    emb = Embed()
    emb.title = "How to use polls 1/2"
    emb.color = get_hex_colour()
    txt1 = "**Basic polls**_\n\
**Adding a new basic poll:**\n\
```!c poll new [title]; [option1]; [option2]; ... [option20]```\n\
The command will select random emotes for reactions. You can leave the title empty, but in that case remember to put a `;` before the first option.\n\
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
You can add as many roles as you need. Input the role as a mention (`@role`) or a role ID if you don't want to mention the role (you can get a role ID by enabling Discord's Developer mode. Then go to `Server Settings` -> `Roles` and copy the ID by right clicking on the role and selecting `Copy ID`. To enable Developer mode, see https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-).\n\
`voteamount` should be an integer.\n\
\n\
**Adding a new advanced poll:**\
```!c poll new -r [title]; [option1]; [option2]; ... [option20]```\n\
Please note that the poll has a character limit of about ~1850 to ~1950 characters depending on how many options you have. Title is not counted into this amount.\n\
\n**For voting help, type:**\n\
```!c vote help```\n\
\n\
**Editing or deleting roles from the database:**\n\
If you want to change how many votes a role has use:\n\
```!c poll editrole [role]:[voteamount],[role]:[voteamount], ...```\n\
Note, that if you change anything in the role you do not need to add or edit the role in the bot's database unless you delete and create a new role in the server settings (i.e. you only need to re-add it if the ID of it changes).\
If you wish to delete a role, use\n\
```!c poll delrole [role], [role], ...```\n\
where `role` is a role ID or a role mention.\n\
Note that you can also delete all roles with the keyword `all`, as in\n\
```!c poll delrole all```"
    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()

    emb.description = txt1
    await dm_channel.send(embed=emb)
    emb.description = txt2
    emb.title = "How to use polls 2/2"
    await dm_channel.send(embed=emb)
    await message.add_reaction("\N{white heavy check mark}")


async def dice_help(ctx):
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
    emb = Embed()
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

async def nitroHelp(message):
    emb = Embed()
    emb.title = "Nitro Tracking 1/2"
    emb.color = get_hex_colour(cora_blonde=True)
    txt = "**General info**\n\
This is the best implementation of nitro tracking that is possible within Discord limitations.\n\
It can track boost amounts, times, and boosters. HOWEVER, it **cannot** continuously check if the boosts are valid. Checks are made either \
automatically when `!c nitro spin` command is used or by using `!c nitro check` manually. These commands however can **only** see _overall_ Nitro status of the user.\n\
It cannot see wheter individual boosts have expired, only if all of them have. Please see these commands below for more info.\n\
**NOTE!!** All commands (besides help) below require administrator priviledges.\n\
\n**Enabling/Disabling nitro tracking on server**\n\
To enable nitro tracking on your server, use\n\
```!c nitro start```\n\
To _ONLY_ show boost announcements but not track boosts, use\n\
```!c nitro notice```\n\
To stop tracking or announcements, use\n\
```!c nitro stop```\n\n\
**Adding boosts manually**\n\
If you have older boosts active on the server, or an error occured during tracking, you can add them manually to the bot's database by using\n\
```!c nitro add [user], [amount], [date]```\n\
_Arguments:_\n\
`user`: Spesifies who the booster is. This can be a mention (@user) or a user ID as an integer.\n\
`amount`: The amount of boosts to add as an integer.\n\
`date`: The date of the boost(s). Date should be in format `DD.MM.YYYY`. This argument is optional. If it is not given, current date will be used.\
If the user is not in the database, this will be added to both the latest and first boost dates. Otherwise the date is compared to the dates\
already in the database and the bot will figure out which one to update."
    txt2 = "**Deleting boosts from database**\n\
The bot will delete expired boosts from database automatically if `spin` or `check` command is used. However, if you wish to delete boost(s) manually,\n\
you can use this command:\n\
```!c nitro del [@user or user ID], [amount or 'all']```\n\
**Exporting the boost database**\n\
This command can only be issued by server owners. This command compiles a CSV-file of all boosters currently in the database and sends it to you via a private message.\n\
_NOTE! You should take a regular backup of your servers nitro boost incase something goes wrong with the bots database._\n\
To use this command type\n\
```!c nitro export```\n\
**Checking Nitro boost statuses**\n\
To check the validity of the nitro boosters in the database, use\n\
```!c nitro check```\n\
_NOTE! As said before, this cannot check individual boost status, only wheter the user is still a nitro booster._\n\
**Nitro spins**\n\
The nitro spin command is basically a bot version of a spin wheel for nitro boosters. This command will pick a random person from the list of nitro boosters. In the default version\
will give more chances for users with more boosts. Meaning, if a user has three boosts, they have three total chances to win.\n\
If you want everyone to have an equal chance of winning regardless of how many boosts they have, add the `-e` flag to the end.\n\
```!c nitro spin [-e]```"

    dm_channel = message.author.dm_channel
    if dm_channel == None:
        dm_channel = await message.author.create_dm()

    emb.description = txt
    await dm_channel.send(embed=emb)
    emb.title = "Nitro Tracking 2/2"
    emb.description = txt2
    await dm_channel.send(embed=emb)
    await message.channel.send(
        "Help message for Nitro commands has been sent via a private message."
    )

async def tirskHelp(message):
    txt = "Saatavilla olevat tirsk komennot:\n\
`count`  Laske vanhat lainaukset\n\
`start`  Aloita kanavan seuraaminen\n\
`stop`   Lopeta kanavan seuraaminen\n\
`export` Vie kaikki lainaukset tietokannasta\n\
`score`  Laske pistetaulu\n\
_Kaikki komennot vaativat 'administrator' oikeudet._"
    emb = Embed()
    emb.title = "Tirsk."
    emb.description = txt
    emb.color = get_hex_colour()

    try:
        await message.channel.send(embed=emb)
    except Forbidden:
        await forbiddenErrorHandler(message)