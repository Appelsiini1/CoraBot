from constants import PREFIX, TRACKED_CHANNELS
from discord import ChannelType, MessageType
from discord.ext import commands
from modules import nitro, tirsk
#from modules import auction
from random import randint
from discord.errors import Forbidden
from modules.common import forbiddenErrorHandler


class MESSAGE_LISTENER(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.morning_messages = [
            "Good morning to you. May every step you make be filled with happiness, love, and peace.",
            "May this morning offer you new hope for life! May you be happy and enjoy every moment of it. Good morning!",
            "Good morning! May your day be filled with positive things and full of blessings. Believe in yourself.",
            "Every morning is a new blessing, a second chance that life gives you because you’re so worth it. Have a great day ahead. Good morning!",
            "Good morning, my friend! Life gives us new opportunities every day, so hoping today will be full of good luck and prosperity for you!",
            "Good Morning, dear! May everything you dreamed about last night comes true!",
            "Good morning beautiful. I hope you have a wonderful day.",
            "Each day is an opportunity to grow. I hope we make the most of it. Wishing you a very good morning.",
            "Every morning brings you new hopes and new opportunities. Don’t miss any one of them while you’re sleeping. Good morning!",
            "Every sunrise marks the rise of life over death, hope over despair, and happiness over suffering. Wishing you a delightful morning today!",
            "Wake up and make yourself a part of this beautiful morning. A beautiful world is waiting outside your door. Have an enjoyable time!",
            "Welcome this beautiful morning with a smile on your face. I hope you’ll have a great day today. Wishing you a very good morning!",
            "The best way to start a day is waking up early in the morning and enjoying nature with a cup of coffee. I hope you’re doing this right now. Good morning!",
            "It’s time to wake up, take a deep breath, and enjoy the sweetness of nature with all your heart. Good morning! Have a good time!",
            "Mornings define our day. It’s all about how we start every morning. So, get up and make a good start of yet another beautiful day. Good morning!",
            "I know you slept tight all night. Now wake up and welcome a new sun so bright, here to make your day right. Good morning!",
            "Good morning to you! May you have a day full of sweet wonders ahead!",
            "Sending you good vibes to start your morning with positive energy! Good morning!",
            "May your day goes as bright as the sun is today! Good morning to you!",
            "Waking up in such a beautiful morning is a guaranty for a day that’s beyond amazing. I hope you’ll make the best of it. Good morning!",
            "Nothing is more refreshing than a beautiful morning that calms your mind and gives you reasons to smile. Good morning! Wishing you a great day.",
            "Another day has just started. Rise and shine like you always do. Wishing you a wonderful morning!",
            "Wake up like the sun every morning and light up the world your awesomeness. You have so many great things to achieve today. Good morning!",
            "Good morning, no matter how hard yesterday was, today is a new beginning, so buckle up and start your day.",
            "I hope this day brightens up your life and makes you energized for work. Good morning!",
            "Wake up like the superstar you are and let the world know you’re not going to stop until you get what you deserve. Good morning my dear!",
            "A new day has come with so many new opportunities for you. Grab them all and make the best out of your day. Here’s me wishing you a good morning!",
            "The darkness of night has ended. A new sun is up there to guide you towards life so bright and blissful. Good morning dear!",
            "Wake up, have your cup of morning tea, and let the morning wind freshen you up like a happiness pill. Wishing you a good morning and a good day ahead!",
            "Wishing you a successful day ahead my dear. You have just received yet another chance to rise and shine like a diamond. Good Morning!",
            "Rise and shine, and get ready for another exciting sunny day! Good morning!",
            "Morning shows the day, so hope you have a really incredible morning today!",
            "You sleep so much that sometimes I wonder why you are not sleeping in a grave already. Good morning to you if you’re still alive!",
            "The sky is awake and the birds have already started working their ass off. But look at you snoring loud!",
            "Your whole life is left for plenty of sleep, but please wake up now and get your lazy bones working! Good morning!",
            "Waking up early in the morning makes you healthier and stronger. Sleeping in the morning makes you lazier and dumber. The choice is yours. Good morning!",
            "Some people wake up at noon and call it a morning. I am wishing you good morning now, so you know when the real morning is!",
            "This is a good morning wish for you if mornings do exist in your life. As far as I know, your day starts at noon and ends at dawn.",
            "Good morning my dear. If you are still sleeping, then you should understand why people call you lazy.",
            "Sleeping late and waking up late are the two biggest enemies of good health. Congratulations to you for doing both like an expert. Good morning!",
            "If there was an Oscar for people who oversleep in the morning, you’d surely win it. But since there is none, you should try waking up early. Good morning!",
            "Nothing about having to wake up in the morning sounds ‘good’, but I still wanna wish you a good morning! May you survive without falling asleep at work!",
            "I’m sure you are all grumpy as usual, but trust me, waking up so early would be worth it today! Good morning and have a productive day!",
            "Getting up early in the morning is the first step of starting a productive day. Good morning, sleepyhead! You have a long way to reach the weekend.",
            "I hope my good morning message doesn’t reach you at 3 p.m.! Have a good day, even if you start your day in the afternoon. Good morning.",
            "Every morning brings us a new opportunity to grab and be successful. So, get up and grab that opportunity. Good Morning!",
            "The sky is awake, birds are awake, wild animals are already up and you are here snoring loud. Good morning sleepyhead!",
            "The night is over and the light has come. As the sun shines for you, wake up and shine for someone else. Good morning!",
            "Life is not all about making a living; it’s all about making an impact. Wake up and impact your life right now. Good Morning!",
            "Success comes to those who seek it. It’s another bright day to chase your dreams. Good morning!",
            "Don’t worry about the mistakes of yesterday, instead, place them under your feet and make miles out of it. Have a nice day!",
            "I hope you have had a nice sleep. It’s now a brand new day for you to try something new. Wake up and keep moving. Good morning!",
            "The morning sun is calling me. I just decided to answer another day. Good morning!",
            "Good morning. Have a cup of coffee and start your engines because it’s still a long way before you reach the weekend.",
            "Smile right when you wake up because soon enough, you’ll realize it’s not a weekend yet. Good morning!",
            "Always harbor positivity in your mind because you will never find it in the real world. Good morning. Have a great day!",
            "Sending you a good morning message in the wake of the day and hoping it’s not the only GOOD you see today.",
            "I was about to say ‘shut up and go to sleep’ to all the early risers, but it’s not socially acceptable. So, good morning!",
            "Good morning to the one who just earned one more day to have the privilege of spending time with me.",
            "Good morning, dear. I know you have so many goals to start the day with. Rising early is not one of them.",
            "I was the richest person in the world, and then it happened. The alarm bell rang. Good morning!",
            "The saddest part of the morning is waking up realizing it’s not a holiday. Gonna spend the whole day with the same old routine. Good morning!",
            "Every morning is a blessing only if you don’t have an alarm clock by your bed. With an alarm clock, it’s a curse. Good morning!",
            "Good morning! If you think you didn’t have enough sleep last night, don’t worry, you still have your chance to take some mid-day naps later.",
            "Wake up and welcome one more unproductive, leisurely day that comes with nothing for you but leaves with a promise of another similar one.",
            "Life is full of stress and troubles. If you want to have a good day, don’t get off your bed. Keep sleeping until you die and stop life happening to you!",
            "If the world was kind to me, it would have slept like an Olympic discipline. Good morning to everyone living in this cruel, unjust world.",
            "You have a message: wake up you lazy.",
            "Good morning dear friend. You’re alive and well, what an unpleasant surprise!",
            "A friend is someone who you think of right when you wake up. Yes, I was thinking of you and wondering if you were alive or not. Good morning!",
            "Wishing you good morning right at the beginning of another stressful day.",
            "I heard you’re having a tough time with your alarm clock. It happens when you’re having an affair with your bed. Good morning dear!",
            "Good morning to you. Good luck with trying to find a good mood today!",
            "You’re definitely not the kind of person who wakes up early in the morning and sends a good morning text to a friend. So, I’m the one who’s playing the role. Good morning!",
            "Sleeping is perhaps the only activity in which you can easily outperform me because it takes no effort, no talent, and no practice. Good morning dear friend!",
        ]  # source: https://www.wishesmsg.com/good-morning-messages-wishes-quotes/ ; https://www.wishesocean.com/good-morning-wishes/ ; https://www.wishesmsg.com/funny-good-morning-wishes-messages/
        self.morning_len = len(self.morning_messages)

    @commands.Cog.listener()
    async def on_message(self, message, *args):
        lower_message = message.content.strip().lower()
        if message.author.bot == True:
            return
        elif message.type in [
            MessageType.premium_guild_subscription,
            MessageType.premium_guild_tier_1,
            MessageType.premium_guild_tier_2,
            MessageType.premium_guild_tier_3,
        ]:
            await nitro.trackNitro(message)
            return
        elif (
            message.channel.type != ChannelType.text
            and message.channel.type != ChannelType.news
        ):
            return
        elif (
            message.content.find("sairasta") != -1
            or message.content.find("ei oo normaalii") != -1
        ):
            msg = "https://cdn.discordapp.com/attachments/693166291468681227/823282434203189258/eioonormaalii.gif"
            await message.channel.send(msg)
            return
        elif (
            lower_message.startswith("morni")
            or lower_message.startswith("good morni")
            or lower_message.startswith("huomenta")
            or lower_message.startswith("hyvää huomenta")
            or lower_message.startswith("mernin")
        ):
            msgIndex = randint(0, self.morning_len - 1)
            msgToSend = self.morning_messages[msgIndex] + " \N{sparkling heart}"
            try:
                await message.channel.send(msgToSend)
            except Forbidden:
                forbiddenErrorHandler(message)
                return
        elif (
            message.channel.id in TRACKED_CHANNELS.channels
            and message.content.startswith(PREFIX) == False
            and message.author != self.bot.user
        ):
            ind = TRACKED_CHANNELS.channels.index(message.channel.id)
            chtype = TRACKED_CHANNELS.types[ind]
            if chtype == 1:
                await tirsk.tirskTrack(message)
                return
            elif chtype == 2:
                #await auction.bid(message)
                return


def setup(client):
    client.add_cog(MESSAGE_LISTENER(client))