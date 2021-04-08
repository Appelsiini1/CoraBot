import logging


async def pressF(message):
    if message.guild.id == 181079344611852288:
        emote_name = "cacF"
        try:
            for em in message.guild.emojis:
                if em.name == emote_name:
                    emoji = em
                    break
            msg = str(emoji)
        except Exception as e:
            logging.exception("Exception in !c f when trying to post 'cacF' emoji.")
            msg = "{} has paid their respects.".format(message.author.display_name)
    else:
        msg = "{} has paid their respects.".format(message.author.display_name)

    await message.channel.send(msg)