from pyrogram import Client, filters
from pyrogram.types import Message
from requests import Session
from urllib.parse import urlparse, parse_qs
from re import findall
import logging

# Bot Credentials
from vars import API_ID, API_HASH, BOT_TOKEN

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.DEBUG)

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

def fetch_links(url):
    details = {"contents": [], "title": "", "total_size": 0}
    
    with Session() as session:
        try:
            _res = session.get(url, cookies=COOKIES)
            logging.debug(f"Initial Response Text: {_res.text}")  

            if not _res.ok:
                raise DirectDownloadLinkException(f"Error fetching URL: {_res.status_code} - {_res.text}")

            jsToken = findall(r'window\.jsToken.*%22(.*)%22', _res.text)
            if not jsToken:
                raise DirectDownloadLinkException("ERROR: jsToken not found!")
            jsToken = jsToken[0]

            surl = parse_qs(urlparse(_res.url).query).get("surl", [])
            if not surl:
                raise DirectDownloadLinkException("ERROR: Could not find surl")
            shortUrl = surl[0]

            params = {
                "app_id": "250528",
                "jsToken": jsToken,
                "shorturl": shortUrl,
                "root": "1"
            }
            
            response = session.get("https://www.1024tera.com/share/list", params=params, cookies=COOKIES)
            logging.debug(f"Raw Response Text: {response.text}")

            try:
                _json = response.json()
                logging.debug(f"Parsed Response JSON: {_json}")
            except ValueError:
                raise DirectDownloadLinkException("ERROR: Response is not valid JSON")

            # Fix: Ensure "_json['list']" exists and is a list before accessing it
            if isinstance(_json, dict) and isinstance(_json.get("list"), list):
                for content in _json["list"]:
                    if isinstance(content, dict) and "isdir" in content:
                        if content["isdir"] in ["1", 1]:
                            logging.info(f"Skipping folder: {content['server_filename']}")
                        else:
                            details["contents"].append({
                                "url": content.get("dlink", ""),
                                "filename": content.get("server_filename", ""),
                                "size": content.get("size", 0)
                            })
                            details["total_size"] += float(content.get("size", 0))
            else:
                raise DirectDownloadLinkException("ERROR: JSON response is not in expected format")

        except Exception as e:
            logging.error(f"Error: {e}")
            raise DirectDownloadLinkException(f"ERROR: {str(e)}")

    return details

def terabox(url):
    details = fetch_links(url)

    if not isinstance(details, dict):  # Fix: Ensure details is a dictionary
        logging.error("fetch_links did not return a dictionary!")
        return "❌ **Error:** Invalid response from server."

    if not details["contents"]:
        return "❌ **Error:** No downloadable content found."

    file_name = f"[Terabox Link]({url})"
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
        logging.debug(f"Command executed successfully")
        message.reply(result, disable_web_page_preview=True)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        message.reply(f"❌ **Error:** {str(e)}")

bot.run()
