from pyrogram import Client, filters
from pyrogram.types import Message
from requests import Session
from urllib.parse import urlparse, parse_qs
from re import findall
import os

# Bot Credentials
from vars import API_ID, API_HASH, BOT_TOKEN

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

class DirectDownloadLinkException(Exception):
    pass

# 🔹 Fresh Cookies (Manually Exported from Browser)
COOKIES = {
    "browserid": "oV3yVUBAotSkMW8ADJymPYDbtqG15hRwCCcrBl3CORYIWatFbhQeOPV6Z_Q=",
    "lang": "en",
    "csrfToken": "MhbJrNNFMhTsyWxM1Q1Un3uQ",
    "__bid_n": "194ff43a22825aa3794207",
    "__stripe_mid": "28201ffd-32ba-441b-8bf5-546807488230a952c1",
    "__stripe_sid": "5b094c70-f997-4aa7-803c-103c17dad0d5e49f60",
    "ndut_fmt": "8148B0F5C88AA31BBA3E58EDC7866849E67F9ADF05CC1CEF9FA47C0FB9454387",
    "ndus": "YQ0oArxteHuixh3XTpWEXoBKdp_oo2PImeTyMOUc"
}

# 🔹 Headers to Avoid Verification
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.1024tera.com/",
    "Connection": "keep-alive"
}

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
            _json = session.get("https://www.1024tera.com/share/list", params=params, headers=HEADERS, cookies=COOKIES).json()
        except Exception as e:
            raise DirectDownloadLinkException(f'ERROR: {e.__class__.__name__}')
        if _json['errno'] not in [0, '0']:
            raise DirectDownloadLinkException(f"ERROR: {_json.get('errmsg', 'Something went wrong!')}")
        
        for content in _json.get("list", []):
            if content['isdir']:
                newFolderPath = os.path.join(folderPath, content['server_filename']) if folderPath else content['server_filename']
                __fetch_links(session, content['path'], newFolderPath)
            else:
                item = {
                    'url': content['dlink'],
                    'filename': content['server_filename'],
                    'path': folderPath,
                }
                details['total_size'] += content.get("size", 0)
                details['contents'].append(item)

    with Session() as session:
        session.cookies.update(COOKIES)
        _res = session.get(url, headers=HEADERS, cookies=COOKIES)

        # 🚨 Check if verification is required
        if "verify" in _res.text.lower():
            raise DirectDownloadLinkException("⚠️ ERROR: Terabox is asking for verification! Try updating cookies.")

        jsToken = findall(r'window\.jsToken.*%22(.*)%22', _res.text)
        if not jsToken:
            raise DirectDownloadLinkException('ERROR: jsToken not found!')
        jsToken = jsToken[0]
        shortUrl = parse_qs(urlparse(_res.url).query).get('surl')
        if not shortUrl:
            raise DirectDownloadLinkException("ERROR: Could not find surl")
        __fetch_links(session)
    
    file_name = f"[{details['title']}]({url})"
    file_size = f"{details['total_size'] / (1024**2):.2f} MB"
    return f"**Title:** {file_name}\n**Size:** `{file_size}`\n**Link:** [Download]({details['contents'][0]['url']})"

@bot.on_message(filters.command("terabox") & filters.private)
def terabox_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return message.reply_text("Please provide a Terabox link!")
    url = message.command[1]
    try:
        response = terabox(url)
        message.reply_text(response, disable_web_page_preview=True)
    except DirectDownloadLinkException as e:
        message.reply_text(str(e))

bot.run()
