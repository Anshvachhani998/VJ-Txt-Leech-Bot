import logging
import requests
import re
from urllib.parse import urlparse, parse_qs
from pyrogram import Client, filters
from pyrogram.types import Message
from vars import API_ID, API_HASH, BOT_TOKEN

# Cookies Configuration
COOKIES = "csrfToken=IBIE5YJHsvqJ5hfy10amPsvU; browserid=ySMpd69WOmpOVcBr8EzVItH__ky9pLg80woRGa9pfYz84x8T0yT5gONXP1g=; lang=en; TSID=AhNUgmZZ4LPb42wLnaq48UqjxmaQyIWJ; __bid_n=194f9a145f6c8074ea4207; _ga=GA1.1.1167242207.1739354886; ndus=Yfszi3CteHuiKo8GYWi0KHQwRCBf3Cybm-JiIY2I; ndut_fmt=CDD95A727FFAF01EA8842D001BBC5CB06A0B69F5D9DDE59F9D8274518871F757; _ga_06ZNKL8C2E=GS1.1.1739354886.1.1.1739355565.57.0.0"
COOKIES_DICT = {i.split('=')[0]: i.split('=')[1] for i in COOKIES.split('; ')}

# Pyrogram Bot Initialization
bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

class TeraboxDownloader:
    def __init__(self, url):
        self.url = url
        self.details = {'contents': [], 'title': '', 'total_size': 0}

    def fetch_links(self):
        session = requests.Session()
        session.cookies.update(COOKIES_DICT)
        
        try:
            _res = session.get(self.url)
        except Exception as e:
            raise Exception(f'ERROR: {e.__class__.__name__}')

        # Extract jsToken
        jsToken_match = re.findall(r'window\.jsToken.*%22(.*)%22', _res.text)
        if not jsToken_match:
            raise Exception('ERROR: jsToken not found!')
        jsToken = jsToken_match[0]

        # Extract short URL
        shortUrl = parse_qs(urlparse(_res.url).query).get('surl')
        if not shortUrl:
            raise Exception("ERROR: Could not find surl")
        shortUrl = shortUrl[0]

        # Fetch File/Folder Details
        self._fetch_links_recursive(session, jsToken, shortUrl)

    def _fetch_links_recursive(self, session, jsToken, shortUrl, dir_='', folderPath=''):
        params = {
            'app_id': '250528',
            'jsToken': jsToken,
            'shorturl': shortUrl
        }
        if dir_:
            params['dir'] = dir_
        else:
            params['root'] = '1'
        
        try:
            _json = session.get("https://www.1024tera.com/share/list", params=params).json()
        except Exception as e:
            raise Exception(f'ERROR: {e.__class__.__name__}')

        if _json['errno'] not in [0, '0']:
            raise Exception(f"ERROR: {_json.get('errmsg', 'Something went wrong!')}")

        if "list" not in _json:
            return
        
        contents = _json["list"]
        for content in contents:
            if content['isdir'] in ['1', 1]:
                newFolderPath = folderPath + '/' + content['server_filename'] if folderPath else content['server_filename']
                self._fetch_links_recursive(session, jsToken, shortUrl, content['path'], newFolderPath)
            else:
                if not self.details['title']:
                    self.details['title'] = content['server_filename']
                file_item = {
                    'url': content['dlink'],
                    'filename': content['server_filename'],
                    'path': folderPath or self.details['title'],
                }
                self.details['total_size'] += int(content.get("size", 0))
                self.details['contents'].append(file_item)

    def get_result(self):
        if not self.details['contents']:
            return "❌ No files found in the given link."
        
        file_name = f"[{self.details['title']}]({self.url})"
        file_size = self.get_readable_file_size(self.details['total_size'])
        return f"┎ **Title:** {file_name}\n┠ **Size:** `{file_size}`\n┖ **Link:** [Download]({self.details['contents'][0]['url']})"

    @staticmethod
    def get_readable_file_size(size):
        if size == 0:
            return "0 B"
        size_name = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size >= 1024 and i < len(size_name) - 1:
            size /= 1024.0
            i += 1
        return f"{size:.2f} {size_name[i]}"

@bot.on_message(filters.command("terabox"))
def terabox_cmd(client, message: Message):
    if len(message.command) < 2:
        message.reply("❌ **Error:** Please provide a Terabox link.\n\n**Usage:** `/terabox <url>`")
        return
    
    url = message.command[1]
    message.reply("🔄 Fetching download link, please wait...")

    try:
        tb = TeraboxDownloader(url)
        tb.fetch_links()
        result = tb.get_result()
        message.reply(result, disable_web_page_preview=True)
    except Exception as e:
        message.reply(f"❌ Error: {str(e)}")

bot.run()
