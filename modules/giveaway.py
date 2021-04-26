import discord
import random
from modules.common import get_hex_colour  # pylint: disable=import-error

EMOJI = "\N{PARTY POPPER}"


async def initiate_giveaway(message):
    if message.author.guild_permissions.administrator:
        msg = (
            "React to this message with the "
            + EMOJI
            + "-emoji to be entered into the giveaway!"
        )
        emb = discord.Embed(title=msg, color=get_hex_colour())
        s_msg = await message.channel.send(embed=emb)
        msg_ID = "Giveaway ID: " + str(s_msg.id)
        emb.set_footer(text=msg_ID)
        await s_msg.edit(embed=emb)
        await s_msg.add_reaction(EMOJI)

    else:
        await message.channel.send(
            "Sorry, you do not have permissions to initiate a giveaway on this server."
        )


async def end_giveaway(message, client_id):
    if message.author.guild_permissions.administrator:
        if len(message.content.split(" ")) <= 2:
            msg = "Usage: !c engiveaway [giveaway_ID]\n(Giveaway ID can be found in the footer of the giveaway message.)"
            emb = discord.Embed(description=msg, color=get_hex_colour(error=True))
            await message.channel.send(embed=emb)
            return
        prefix = "!c endgiveaway "
        args = message.content[len(prefix) - 1 :].strip().lstrip("[").rstrip("]")
        react = await message.channel.fetch_message(args)
        list_user = await react.reactions[0].users().flatten()
        random_n = random.randint(0, len(list_user) - 1)
        if len(list_user) == 1:
            await message.channel.send("No entries to the giveaway :(")
            return
        while True:
            winner_id = list_user[random_n].id
            if winner_id != client_id:
                break
            if winner_id == client_id:
                random_n = random.randint(0, len(list_user) - 1)
        mention_str = "<@" + str(winner_id) + ">"
        w_msg = (
            "**Gongratulations "
            + mention_str
            + " you are the winner of the giveaway!** "
            + EMOJI
            + EMOJI
        )
        await message.channel.send(w_msg)
    else:
        await message.channel.send(
            "Sorry, you do not have permissions to end a giveaway on this server."
        )
