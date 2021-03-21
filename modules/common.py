import random
import discord
import sys
import os
import logging

def get_hex_colour(cora_blonde=False, cora_eye=False):
    """Returns a hex colour as a discord.Colour object
Args: cora_blonde = [True|False] Default: False
cora_eye = [True|False] Default: False"""
    if cora_blonde == True:
        color = discord.Colour(value=0xffcc99)
        return color
    elif cora_eye == True:
        color = discord.Colour(value=0x338b41)
        return color
    else:
        random_n = random.randint(0,16777215)
        hex_n = discord.Colour(value=random_n)
        return hex_n
        
# async def exit_bot(message, exit_code):
#     prefixs = "!c exit"
#     arg = message.content.replace(prefixs, "").strip()
#     print(arg)
#     if arg == exit_code:
#         await message.channel.send("The bot will now quit.")
#         sys.exit(0)
#     else:
#         await message.channel.send("What was that?")
         

def get_tokens():
    """Gets environment variables. Returns a list."""
    try:
        with open(".env", "r") as f:
            tokens = f.readlines()
    except Exception:
        print("Could not acquire environment variables. Stopping.")
        sys.exit(1)
    return tokens