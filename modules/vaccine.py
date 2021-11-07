import json
from discord.errors import Forbidden
from discord.ext import commands
import requests
import discord
from modules.common import forbiddenErrorHandler, get_hex_colour, check_if_channel, check_if_bot
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

ALUEET_INDEX = [
    "518362",
    "184144",
    "518294",
    "518309",
    "518306",
    "518320",
    "518377",
    "518303",
    "518340",
    "518369",
    "518295",
    "518335",
    "518322",
    "518353",
    "518298",
    "518343",
    "518354",
    "518351",
    "518300",
    "518366",
    "518323",
    "518349",
    "518327",
]

QUERY = {
    "query": [
        {
            "code": "Alue",
            "selection": {
                "filter": "item",
                "values": [
                    "SSS",  # koko maa 0
                    "KU405",  # lappeenranta 1
                    "SHP09",  # EK SHP 2
                    "SHP15",  # EP SHP 3
                    "SHP10",  # ES SHP 4
                    "SHP25",  # HUS SHP 5
                    "SHP11",  # IS SHP 6
                    "SHP19",  # K SHP 7
                    "SHP05",  # KH SHP 8
                    "SHP17",  # KP SHP 9
                    "SHP14",  # KS SHP 10
                    "SHP08",  # Kymi SHP 11
                    "SHP21",  # Lapin SHP 12
                    "SHP20",  # LP SHP 13
                    "SHP06",  # Pirkan SHP 14
                    "SHP12",  # PK SHP 15
                    "SHP18",  # PP SHP 16
                    "SHP13",  # PS SHP 17
                    "SHP07",  # PH SHP 18
                    "SHP04",  # SK SHP 19
                    "SHP16",  # Vaasa SHP 20
                    "SHP03",  # VS SHP 21
                    "SHP00",  # Ahvenanmaa 22
                ],
            },
        },
        {"code": "Tiedot", "selection": {"filter": "item", "values": ["vaesto"]}},
        {"code": "Vuosi", "selection": {"filter": "item", "values": ["2020"]}},
    ],
    "response": {"format": "json-stat2"},
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
        response3 = requests.post(
            "https://pxnet2.stat.fi:443/PXWeb/api/v1/fi/StatFin/vrm/vaerak/statfin_vaerak_pxt_11ra.px",
            headers={"User-Agent": "Appelsiini1:n Discord Botti"},
            json=QUERY,
        )
        if (
            response.status_code == 200
            and response2.status_code == 200
            and response3.status_code == 200
        ):
            json_data = json.loads(response.text)
            vacc_data = json_data["dataset"]["value"].items()
            pop_data = (
                json.loads(response3.text)["value"][ALUEET_INDEX.index(param)]
                if param != "518333"
                else 0
            )
            one_dose = 0
            for keypair in vacc_data:
                one_dose = keypair[1]
            json_data = json.loads(response2.text)
            vacc_data = json_data["dataset"]["value"].items()
            two_doses = 0
            for keypair in vacc_data:
                two_doses = keypair[1]
            return one_dose, two_doses, pop_data

        else:
            msg = "Could not fetch vaccination data, server responded with code {0} and {1} and {2}.".format(
                response.status_code, response2.status_code, response3.status_code
            )
            logging.error(msg)
            msg2 = f"PARAM = {param}"
            logging.error(msg2)
            logging.error(response.content)
            logging.error(response2.content)
            logging.error(response3.content)
            return msg, msg2

    def makeEmbed(self, one_dose, two_doses, emb, pop_data, areaCode="Finland"):
        if two_doses.startswith("PARAM"):
            emb.description = one_dose
            emb.color = get_hex_colour(error=True)
        else:
            if areaCode != "Finland":
                area = ALUEET[areaCode]
            else:
                area = "Finland"
            emb.title = f"Current number of COVID-19 vaccinated people in {area}:"
            emb.description = f"One dose: {one_dose} ({round((int(one_dose)/int(pop_data))*100)}% of area population)\nTwo doses: {two_doses} ({round((int(two_doses)/int(pop_data))*100)}% of area population)"
            emb.color = get_hex_colour(cora_eye=True)
            emb.set_footer(
                text=f"Source: Finnish Institute for Health and Welfare (THL.fi) and Statistics Finland (tilastokeskus.fi)"
            )
        return emb

    @commands.command(name="vacc")
    @commands.check(check_if_channel)
    @commands.check(check_if_bot)
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
            one_dose, two_doses, pop_data = self.getVaccineInfo("518362")
            emb = self.makeEmbed(one_dose, two_doses, emb, pop_data)
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
                one_dose, two_doses, pop_data = self.getVaccineInfo(param)
                emb = self.makeEmbed(one_dose, two_doses, emb, pop_data, areaCode=param)
                await s_msg.edit(embed=emb)


def setup(client):
    client.add_cog(Vaccine(client))