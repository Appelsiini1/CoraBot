import random
import discord
from discord.ext import commands
from modules.common import get_hex_colour, check_if_channel, check_if_bot


class MOOD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.moods = {
            0: "happy",
            1: "sad",
            2: "alone",
            3: "scared",
            4: "horny",
            5: "depressed",
            6: "angry",
            7: "anxious",
            8: "friendly",
            9: "optimistic",
            10: "romantic",
            11: "mischievous"
        }

    @commands.command()
    @commands.check(check_if_channel)
    @commands.check(check_if_bot)
    async def mood(self, ctx, *arg):
        happy = random.randint(0, 100)
        sad = random.randint(0, 100)
        alone = random.randint(0, 100)
        scared = random.randint(0, 100)
        horny = random.randint(0, 100)
        depressed = random.randint(0, 100)
        angry = random.randint(0, 100)
        anxious = random.randint(0, 100)
        friendly = random.randint(0, 100)
        optimistic = random.randint(0, 100)
        romantic = random.randint(0, 100)
        mischievous = random.randint(0, 100)

        mood_list = [happy, sad, alone, scared, horny, depressed, angry, anxious, friendly, optimistic, romantic, mischievous]
        mood = random.randint(0, len(mood_list)-1)
        mood_p = mood_list[mood]
        mood_name = self.moods[mood]
        
        msg = f"{ctx.author.mention}** you are {mood_p}% {mood_name}.**"

        
        await ctx.send(msg)


def setup(client):
    client.add_cog(MOOD(client))