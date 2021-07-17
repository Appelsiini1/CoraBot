import json
from discord import embeds
from discord.errors import Forbidden
from discord.ext import commands
import requests
import discord
from modules.common import forbiddenErrorHandler, get_hex_colour
import logging

ALUEET = {
    "518327": "Ahvenanmaa",
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
    "518362": "Kaikki alueet",
    "184144": "Lappeenranta",
}


class Vaccine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def getVaccineInfo(self, param):
        response = requests.get(
            f"https://sampo.thl.fi/pivot/prod/fi/vaccreg/cov19cov/fact_cov19cov.json?row=cov_vac_dose-533170&row=area-{param}",
            headers={"User-Agent": "Appelsiini1:n Discord Botti"},
        )
        response2 = requests.get(
            f"https://sampo.thl.fi/pivot/prod/fi/vaccreg/cov19cov/fact_cov19cov.json?row=cov_vac_dose-533164&row=area-{param}",
            headers={"User-Agent": "Appelsiini1:n Discord Botti"},
        )
        if response.status_code == 200 and response2.status_code == 200:
            json_data = json.loads(response.text)
            vacc_data = json_data["dataset"]["value"].items()
            one_dose = 0
            for keypair in vacc_data:
                one_dose = keypair[1]
            json_data = json.loads(response2.text)
            vacc_data = json_data["dataset"]["value"].items()
            two_doses = 0
            for keypair in vacc_data:
                two_doses = keypair[1]
            return one_dose, two_doses

        else:
            msg = "Could not fetch vaccination data, server responded with code {0} and {1}.".format(
                response.status_code, response2.status_code
            )
            logging.error(msg)
            msg2 = f"PARAM = {param}"
            logging.error(msg2)
            logging.error(response.content)
            return msg, msg2

    def makeEmbed(self, one_dose, two_doses, emb, areaCode="Finland"):
        if two_doses.startswith("PARAM"):
            emb.description = one_dose
            emb.color = get_hex_colour(error=True)
        else:
            if areaCode != "Finland":
                area = ALUEET[areaCode]
            else:
                area = "Finland"
            emb.title = f"Current number of COVID-19 vaccinated people in {area}:"
            emb.description = f"One dose: {one_dose}\nTwo doses: {two_doses}"
            emb.color = get_hex_colour(cora_eye=True)
            emb.set_footer(
                text=f"Source: Finnish Institute for Health and Welfare (THL.fi)"
            )
        return emb

    async def sendVaccInfo(self, ctx):
        emb = discord.Embed(
            description="_Getting latest vaccine data from THL..._",
            color=get_hex_colour(),
        )
        try:
            s_msg = await ctx.send(embed=emb)
        except Forbidden:
            await forbiddenErrorHandler(ctx.message)
        if len(ctx.message.content.split(" ")) == 2:
            one_dose, two_doses = self.getVaccineInfo("518362")
            emb = self.makeEmbed(one_dose, two_doses, emb)
            await s_msg.edit(embed=emb)

        elif len(ctx.message.content.split(" ")) > 2:
            param = ctx.message.content[7:].strip().lstrip("[").rstrip("]")
            if param == "help":
                emb.title = "Available areas:"
                txt = ""
                for keypair in ALUEET.items():
                    txt = txt + keypair[0] + ": " + keypair[1] + "\n"
                emb.description = txt
                await s_msg.edit(embed=emb)
                return

            else:
                try:
                    ALUEET[param]
                except KeyError:
                    emb.description = "Area code does not match any known areas. Please provide a valid code or leave empty for all areas.\
                    \nType `!c vacc help` for all currently available areas."
                    emb.color = get_hex_colour(error=True)
                    await s_msg.edit(embed=emb)
                    return
                one_dose, two_doses = self.getVaccineInfo(param)
                emb = self.makeEmbed(one_dose, two_doses, emb, areaCode=param)
                await s_msg.edit(embed=emb)


def setup(client):
    client.add_cog(Vaccine(client))