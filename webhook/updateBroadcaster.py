import requests
import logging


def main():
    logging.basicConfig(
        filename="broadcaster_log.txt",
        level=logging.INFO,
        format="%(asctime)s %(levelname)s - %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )

    with open("urls.txt", "r") as f:
        urls = f.readlines()

    with open("versions.txt", "r") as f:
        txtFromFile = f.readline()
        if txtFromFile.startswith("v"):
            title = f"New version of CoraBot is live!"
            version = txtFromFile
            txtFromFile = f.readline()

        text = f"**{version}**\n"
        while txtFromFile.strip() != "###":
            text += txtFromFile
            txtFromFile = f.readline()

    # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
    data = {
        "username": "CoraBot Updates",
        "avatar_url": "https://media.discordapp.net/attachments/693166291468681227/851120811393417216/cora_pfp_update_pride.png",
    }

    # for all params, see https://discordapp.com/developers/docs/resources/channel#embed-object
    data["embeds"] = [{"description": text, "title": title}]

    for i, url in enumerate(urls):
        if url.strip() == "":
            continue
        if url.startswith("##"):
            continue
        result = requests.post(url.strip(), json=data)

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError:
            logging.exception("Error occured while sending message:")
        else:
            logging.info(
                f"Payload {i} delivered successfully, code {result.status_code}."
            )


if __name__ == "__main__":
    main()