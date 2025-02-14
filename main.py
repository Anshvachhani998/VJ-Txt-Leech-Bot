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


# Logging setup
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

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
            
            # Log the response type and content before trying to parse it
            logging.debug(f"Response Type: {type(response)}")
            logging.debug(f"Response Text: {response.text}")

            # Check if response is JSON
            try:
                _json = response.json()
                logging.debug(f"Response JSON: {_json}")
            except Exception as e:
                logging.error(f"Failed to parse JSON: {e}")
                raise DirectDownloadLinkException(f"ERROR: Failed to parse JSON from response.")
                
        except Exception as e:
            logging.error(f"Network Error: {e}")
            raise DirectDownloadLinkException(f"ERROR: {e.__class__.__name__}")

        if _json.get("errno") not in [0, "0"]:
            errmsg = _json.get("errmsg", "Something went wrong!")
            logging.error(f"API Error: {errmsg}")
            raise DirectDownloadLinkException(f"ERROR: {errmsg}")

        for content in _json.get("list", []):
            if content["isdir"] in ["1", 1]:
                newFolderPath = path.join(folderPath, content["server_filename"]) if folderPath else content["server_filename"]
                __fetch_links(session, content["path"], newFolderPath)
            else:
                item = {
                    "url": content["dlink"],
                    "filename": content["server_filename"],
                    "path": folderPath or content["server_filename"],
                }
                details["total_size"] += float(content.get("size", 0))
                details["contents"].append(item)

    with Session() as session:
        try:
            # Fetching the page content
            _res = session.get(url, cookies=COOKIES)
            logging.debug(f"Response Text: {_res.text}")
            
            # Check if response is as expected
            if not _res.ok:
                raise DirectDownloadLinkException(f"Error fetching URL: {_res.status_code} - {_res.text}")
            
            # Extracting jsToken
            jsToken = findall(r'window\.jsToken.*%22(.*)%22', _res.text)
            logging.debug(f"jsToken found: {jsToken}")
            if not jsToken:
                raise DirectDownloadLinkException("ERROR: jsToken not found!")
            jsToken = jsToken[0]
            
            # Extracting shortUrl
            surl = parse_qs(urlparse(_res.url).query).get("surl", [])
            logging.debug(f"surl found: {surl}")
            if len(surl) > 0:
                shortUrl = surl[0]
                logging.debug(f"shortUrl found: {shortUrl}")
            else:
                raise DirectDownloadLinkException("ERROR: Could not find surl")
            
            __fetch_links(session)
        except Exception as e:
            logging.error(f"Error: {e}")
            raise DirectDownloadLinkException(f"ERROR: {str(e)}")

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
        message.reply(result, disable_web_page_preview=True)
    except Exception as e:
        message.reply(f"❌ **Error:** {str(e)}")



bot.run()
