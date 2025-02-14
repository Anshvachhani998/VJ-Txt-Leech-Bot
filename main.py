from pyrogram import Client, filters
from pyrogram.types import Message
from requests import Session
from urllib.parse import urlparse, parse_qs
from re import findall
import os
import requests


# Bot Credentials
from vars import API_ID, API_HASH, BOT_TOKEN

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

import logging
from os import path
from requests import Session
from urllib.parse import urlparse, parse_qs
from re import findall
from pyrogram import Client, filters


logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


class DirectDownloadLinkException(Exception):
    pass

COOKIES = "csrfToken=IBIE5YJHsvqJ5hfy10amPsvU; browserid=ySMpd69WOmpOVcBr8EzVItH__ky9pLg80woRGa9pfYz84x8T0yT5gONXP1g=; lang=en; TSID=AhNUgmZZ4LPb42wLnaq48UqjxmaQyIWJ; __bid_n=194f9a145f6c8074ea4207; _ga=GA1.1.1167242207.1739354886; ndus=Yfszi3CteHuiKo8GYWi0KHQwRCBf3Cybm-JiIY2I; ndut_fmt=CDD95A727FFAF01EA8842D001BBC5CB06A0B69F5D9DDE59F9D8274518871F757; _ga_06ZNKL8C2E=GS1.1.1739354886.1.1.1739355565.57.0.0"


def get_readable_file_size(size):
    """Converts bytes to human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"

def terabox(url):
    details = {"contents": [], "title": "", "total_size": 0}
    
    def __fetch_links(session, dir_="", folderPath=""):
        params = {
            "app_id": "250528",
            "jsToken": jsToken,
            "shorturl": shortUrl,
        }
        if dir_:
            params["dir"] = dir_
        else:
            params["root"] = "1"
        try:
            response = session.get("https://www.1024tera.com/share/list", params=params, cookies=COOKIES)

            # Send the raw response as it is to see what we get
            return response.text

        except Exception as e:
            logging.error(f"Error: {e}")
            raise DirectDownloadLinkException(f"ERROR: {str(e)}")

    with Session() as session:
        try:
            _res = session.get(url, cookies=COOKIES)

            # Send the initial response text as it is
            return _res.text

        except Exception as e:
            logging.error(f"Error: {e}")
            raise DirectDownloadLinkException(f"ERROR: {str(e)}")

    # Return the file name and size info if everything works correctly (just for confirmation)
    file_name = f"[{details['title']}]({url})"
    file_size = get_readable_file_size(details["total_size"])
    return f"📂 **Title:** {file_name}\n📏 **Size:** `{file_size}`\n🔗 **Link:** [Download]({details['contents'][0]['url']})"




@bot.on_message(filters.command("terabox"))
def terabox_cmd(client, message):
    if len(message.command) < 2:
        message.reply("❌ **Error:** Please provide a Terabox link.\n\n**Usage:** `/terabox <url>`")
        return

    url = message.command[1]
    
    try:
        message.reply("🔄 Fetching download link, please wait...")
        result = terabox(url)
        print("Done")
        message.reply(result, disable_web_page_preview=True)
    except Exception as e:
        message.reply(f"❌ **Error:** {str(e)}")



bot.run()
