import logging
import requests
import re
from urllib.parse import urlparse, parse_qs
from pyrogram import Client, filters
from pyrogram.types import Message
from vars import API_ID, API_HASH, BOT_TOKEN
from requests import Session

# ✅ Cookies ko dictionary me convert karna
cookies = "csrfToken=IBIE5YJHsvqJ5hfy10amPsvU; browserid=ySMpd69WOmpOVcBr8EzVItH__ky9pLg80woRGa9pfYz84x8T0yT5gONXP1g=; lang=en; TSID=AhNUgmZZ4LPb42wLnaq48UqjxmaQyIWJ"
COOKIES_DICT = {i.split('=')[0]: i.split('=')[1] for i in cookies.split('; ')}

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
logging.basicConfig(level=logging.INFO)

def terabox(url):
    details = {'contents': [], 'title': '', 'total_size': 0}

    def __fetch_links(session, dir_='', folderPath=''):
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
            _json = session.get("https://www.1024tera.com/share/list", params=params, cookies=COOKIES_DICT).json()
        except Exception as e:
            raise Exception(f'ERROR: {e.__class__.__name__}')
        
        if _json.get('errno') not in [0, '0']:
            raise Exception(f"ERROR: {_json.get('errmsg', 'Something went wrong!')}")

        if "list" not in _json:
            return
        
        for content in _json["list"]:
            if content['isdir'] in ['1', 1]:
                newFolderPath = folderPath + "/" + content['server_filename'] if folderPath else content['server_filename']
                __fetch_links(session, content['path'], newFolderPath)
            else:
                folderPath = folderPath or details['title'] or content['server_filename']
                details['contents'].append({
                    'url': content['dlink'],
                    'filename': content['server_filename'],
                    'path': folderPath
                })
                details['total_size'] += int(content.get("size", 0))

    with Session() as session:
        try:
            _res = session.get(url, cookies=COOKIES_DICT)
        except Exception as e:
            raise Exception(f'ERROR: {e.__class__.__name__}')
        
        jsToken = re.findall(r'window\.jsToken.*%22(.*)%22', _res.text)
        if not jsToken:
            raise Exception('ERROR: jsToken not found!.')
        jsToken = jsToken[0]

        shortUrl = parse_qs(urlparse(_res.url).query).get('surl')
        if not shortUrl:
            raise Exception("ERROR: Could not find surl")
        
        __fetch_links(session)

    file_name = f"[{details['title']}]({url})"
    file_size = details['total_size']
    return f"┎ **Title:** {file_name}\n┠ **Size:** `{file_size}` bytes\n┖ **Link:** [Link]({details['contents'][0]['url']})"

@bot.on_message(filters.command("terabox"))
def terabox_cmd(client, message: Message):
    if len(message.command) < 2:
        message.reply("❌ **Error:** Please provide a Terabox link.\n\n**Usage:** `/terabox <url>`")
        return
    url = message.command[1]
    message.reply("🔄 Fetching download link, please wait...")
    try:
        result = terabox(url)
        message.reply(result, disable_web_page_preview=True)
    except Exception as e:
        message.reply(f"❌ **Error:** {str(e)}", disable_web_page_preview=True)

bot.run()
