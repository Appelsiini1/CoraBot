import discord
import random
from discord.ext import commands
from modules.common import get_hex_colour

EMOJI = "\N{PARTY POPPER}"

class Giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="giveaway")
    async def initiate_giveaway(self, ctx):
        if ctx.author.guild_permissions.administrator:
            msg = (
                "React to this message with the "
                + EMOJI
                + "-emoji to be entered into the giveaway!"
            )
            emb = discord.Embed(title=msg, color=get_hex_colour())
            s_msg = await ctx.send(embed=emb)
            msg_ID = "Giveaway ID: " + str(s_msg.id)
            emb.set_footer(text=msg_ID)
            await s_msg.edit(embed=emb)
            await s_msg.add_reaction(EMOJI)

        else:
            await ctx.send(
                "Sorry, you do not have permissions to initiate a giveaway on this server."
            )

    @commands.command(name="endgiveaway")
    async def end_giveaway(self, ctx):
        if ctx.author.guild_permissions.administrator:
            if len(ctx.message.content.split(" ")) <= 2:
                msg = "Usage: !c engiveaway [giveaway_ID]\n(Giveaway ID can be found in the footer of the giveaway message.)"
                emb = discord.Embed(description=msg, color=get_hex_colour(error=True))
                await ctx.send(embed=emb)
                return
            prefix = "!c endgiveaway "
            args = ctx.message.content[len(prefix) - 1 :].strip().lstrip("[").rstrip("]")
            react = await ctx.channel.fetch_message(args)
            list_user = await react.reactions[0].users().flatten()
            random_n = random.randint(0, len(list_user) - 1)
            if len(list_user) == 1:
                await ctx.send("No entries to the giveaway :(")
                return
            client_id = self.bot.user.id
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
            await ctx.send(w_msg)
        else:
            await ctx.send(
                "Sorry, you do not have permissions to end a giveaway on this server."
            )

def setup(client):
    client.add_cog(Giveaway(client))