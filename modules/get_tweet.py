import tweepy
import discord
import logging
import random

MAX_ITEMS = 100

async def get_tweet(message, auth):
    api = tweepy.API(auth)

    twitter_handle = message.content.split(" ")[2]
    cursor = tweepy.Cursor(api.user_timeline, id=twitter_handle).items(MAX_ITEMS)

    random_n = random.randint(0, 99)

    for i in range(0, random_n):
        tweet = cursor.next()

    #time = datetime.datetime.today().strftime("%d.%m.%Y")

    