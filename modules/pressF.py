async def pressF(message):
    msg = "{} has paid their respects.".format(message.author.display_name)

    await message.channel.send(msg)