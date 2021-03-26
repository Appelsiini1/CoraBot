import json
from discord import embeds
import requests
import discord
from modules.common import get_hex_colour
import logging

ALUEET = {"518327": "Ahvenanmaa",
"518294": "Etelä-Karjalan SHP",
"518309": "Etelä-Pohjanmaan SHP",
"518306": "Etelä-Savon SHP",
"518320": "Helsingin ja Uudenmaan SHP",
"518377": "Itä-Savon SHP",
"518303": "Kainuun SHP",
"518340": "Kanta-Hämeen SHP",
"518369": "Keski-Pohjanmaan SHP",
"518295": "Keski-Suomen SHP",
"518335": "Kymenlaakson SHP",
"518322": "Lapin SHP",
"518353": "Länsi-Pohjan SHP",
"518298": "Pirkanmaan SHP",
"518343": "Pohjois-Karjalan SHP",
"518354": "Pohjois-Pohjanmaan SHP",
"518351": "Pohjois-Savon SHP",
"518300": "Päijät-Hämeen SHP",
"518366": "Satakunnan SHP",
"518323": "Vaasan SHP",
"518349": "Varsinais-Suomen SHP",
"518333": "Muut alueet",
"518362": "Kaikki alueet"}

async def getVaccineInfo(message):
    emb = discord.Embed(description="_Getting latest vaccine data from THL..._", color=get_hex_colour())
    s_msg = await message.channel.send(embed=emb)
    if len(message.content.split(" ")) == 2:
        response = requests.get("https://sampo.thl.fi/pivot/prod/fi/vaccreg/cov19cov/fact_cov19cov.json?row=area-518362", headers={'User-Agent': "Appelsiini1:n Discord Botti"})
        if response.status_code == 200:
            json_data = json.loads(response.text)
            vacc_data = json_data["dataset"]["value"].items()
            value = 0
            for keypair in vacc_data:
                value = keypair[1]
            emb.description=f"**Current number of people that have received at least one dose of COVID-19 vaccine in Finland:\n** {value}"
            emb.color=get_hex_colour(cora_eye=True)
            emb.set_footer(text="Source: THL.fi")
            await s_msg.edit(embed=emb)
        else:
            msg = "Could not fetch vaccination data, server responded with code {}.".format(response.status_code)
            emb.description=msg
            logging.error(msg)
            logging.error(response.content)
            await s_msg.edit(embed=emb)
    elif len(message.content.split(" ")) > 2:
        param = message.content[7:].strip()
        if param == "help":
            emb.title="Available areas:"
            txt = ""
            for keypair in ALUEET.items():
                txt = txt + keypair[0] + ": " + keypair[1] + "\n"
            emb.description=txt
            await s_msg.edit(embed=emb)
            return
        
        try:
            ALUEET[param]
        except KeyError:
            emb.description="Area code does not match any known areas. Please provide a valid code or leave empty for all areas.\
            \nType '!c vacc help' for all currently available areas."
            emb.color=0xFF0000
            await s_msg.edit(embed=emb)
            return
        
        response = requests.get(f"https://sampo.thl.fi/pivot/prod/fi/vaccreg/cov19cov/fact_cov19cov.json?row=area-{param}", headers={'User-Agent': "Appelsiini1:n Discord Botti"})
        if response.status_code == 200:
            json_data = json.loads(response.text)
            vacc_data = json_data["dataset"]["value"].items()
            value = 0
            for keypair in vacc_data:
                value = keypair[1]
            emb.description=f"**Current number of people that have received at least one dose of COVID-19 vaccine in {ALUEET[param]}:\n** {value}"
            emb.color=get_hex_colour(cora_eye=True)
            emb.set_footer(text="Source: THL.fi")
            await s_msg.edit(embed=emb)
        else:
            msg = "Could not fetch vaccination data, server responded with code {}.".format(response.status_code)
            emb.description=msg
            logging.error(msg)
            msg2= f"PARAM = {param}"
            logging.error(msg2)
            logging.error(response.content)
            await s_msg.edit(embed=emb)