import logging
import requests
import re
from urllib.parse import urlparse, parse_qs
from pyrogram import Client, filters
from pyrogram.types import Message
from vars import API_ID, API_HASH, BOT_TOKEN

COOKIES = "csrfToken=IBIE5YJHsvqJ5hfy10amPsvU; browserid=ySMpd69WOmpOVcBr8EzVItH__ky9pLg80woRGa9pfYz84x8T0yT5gONXP1g=; lang=en; TSID=AhNUgmZZ4LPb42wLnaq48UqjxmaQyIWJ; __bid_n=194f9a145f6c8074ea4207; _ga=GA1.1.1167242207.1739354886; ndus=Yfszi3CteHuiKo8GYWi0KHQwRCBf3Cybm-JiIY2I; ndut_fmt=CDD95A727FFAF01EA8842D001BBC5CB06A0B69F5D9DDE59F9D8274518871F757; _ga_06ZNKL8C2E=GS1.1.1739354886.1.1.1739355565.57.0.0"

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

class TeraboxDownloader:
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.jsToken = None
        self.shortUrl = None
        self.err = None
        self.errno = None
        self.json = None
        self.details = {"contents": [], "title": "", "total_size": 0}
        self.extract_tokens()

    def extract_tokens(self):
        try:
            response = self.session.get(self.url, cookies=COOKIES)
            logging.debug(f"Initial Response Text: {response.text}")
            jsToken_match = re.findall(r'window\\.jsToken.*%22(.*)%22', response.text)
            if not jsToken_match:
                self.err = "ERROR: jsToken not found!"
                return
            self.jsToken = jsToken_match[0]
            surl = parse_qs(urlparse(response.url).query).get("surl", [])
            if surl:
                self.shortUrl = surl[0]
            else:
                self.err = "ERROR: Could not find surl"
        except Exception as e:
            self.err = f"ERROR: {str(e)}"

    def fetch_links(self, dir_="", folderPath=""):
        if not self.jsToken:
            self.err = "ERROR: Missing jsToken"
            return
        params = {"app_id": "250528", "jsToken": self.jsToken}
        if dir_:
            params["dir"] = dir_
        else:
            params["root"] = "1"
        try:
            response = self.session.get("https://www.1024tera.com/share/list", params=params, cookies=COOKIES)
            self.json = response.json()
        except Exception as e:
            self.err = f"ERROR: {e.__class__.__name__}"
            return
        if self.json.get("errno") not in [0, "0"]:
            self.err = self.json.get("errmsg", "Unknown error")
            self.errno = self.json["errno"]

    def get_result(self):
        if self.err:
            return f"❌ {self.err}"
        return f"✅ Fetched links successfully: {self.json}"

@bot.on_message(filters.command("terabox"))
def terabox_cmd(client, message: Message):
    if len(message.command) < 2:
        message.reply("❌ **Error:** Please provide a Terabox link.\n\n**Usage:** `/terabox <url>`")
        return
    url = message.command[1]
    message.reply("🔄 Fetching download link, please wait...")
    tb = TeraboxDownloader(url)
    tb.fetch_links()
    result = tb.get_result()
    message.reply(result, disable_web_page_preview=True)

bot.run()
