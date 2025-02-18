from pyrogram import Client, filters
from pyrogram.types import Message
from requests import Session
import logging
import re
import requests

# Bot Credentials
from vars import API_ID, API_HASH, BOT_TOKEN

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

COOKIES = "csrfToken=IBIE5YJHsvqJ5hfy10amPsvU; browserid=ySMpd69WOmpOVcBr8EzVItH__ky9pLg80woRGa9pfYz84x8T0yT5gONXP1g=; lang=en; TSID=AhNUgmZZ4LPb42wLnaq48UqjxmaQyIWJ; __bid_n=194f9a145f6c8074ea4207; _ga=GA1.1.1167242207.1739354886; ndus=Yfszi3CteHuiKo8GYWi0KHQwRCBf3Cybm-JiIY2I; ndut_fmt=CDD95A727FFAF01EA8842D001BBC5CB06A0B69F5D9DDE59F9D8274518871F757; _ga_06ZNKL8C2E=GS1.1.1739354886.1.1.1739355565.57.0.0"

# Terabox cookie and headers
HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
}

class TeraboxFile:
    def __init__(self):
        self.r = requests.Session()
        self.headers = HEADERS
        self.result = {'status': 'failed', 'js_token': '', 'browser_id': '', 'cookie': '', 'sign': '', 'timestamp': '', 'shareid': '', 'uk': '', 'list': []}

    def search(self, url):
        req = self.r.get(url, allow_redirects=True)
        self.short_url = re.search(r'surl=([^ &]+)', str(req.url)).group(1)
        self.getAuthorization()
        self.getMainFile()

    def getAuthorization(self):
        url = f'https://www.terabox.app/wap/share/filelist?surl={self.short_url}'
        req = self.r.get(url, headers=self.headers, allow_redirects=True)
        js_token = re.search(r'%28%22(.*?)%22%29', str(req.text.replace('\\', ''))).group(1)
        browser_id = req.cookies.get_dict().get('browserid')
        cookie = 'lang=id;' + ';'.join([f'{a}={b}' for a, b in self.r.cookies.get_dict().items()])
        self.result['js_token'] = js_token
        self.result['browser_id'] = browser_id
        self.result['cookie'] = cookie

    def getMainFile(self):
        url = f'https://www.terabox.com/api/shorturlinfo?app_id=250528&shorturl=1{self.short_url}&root=1'
        req = self.r.get(url, headers=self.headers, cookies={'cookie': ''}).json()
        all_file = self.packData(req, self.short_url)
        if len(all_file):
            self.result['sign'] = req['sign']
            self.result['timestamp'] = req['timestamp']
            self.result['shareid'] = req['shareid']
            self.result['uk'] = req['uk']
            self.result['list'] = all_file
            self.result['status'] = 'success'

    def packData(self, req, short_url):
        all_file = [{
            'is_dir': item['isdir'],
            'path': item['path'],
            'fs_id': item['fs_id'],
            'name': item['server_filename'],
            'type': self.checkFileType(item['server_filename']) if not bool(int(item.get('isdir'))) else 'other',
            'size': item.get('size') if not bool(int(item.get('isdir'))) else '',
            'image': item.get('thumbs', {}).get('url3', '') if not bool(int(item.get('isdir'))) else '',
            'list': self.getChildFile(short_url, item['path'], '0') if item.get('isdir') else [],
        } for item in req.get('list', [])]
        return all_file

    def getChildFile(self, short_url, path='', root='0'):
        params = {'app_id': '250528', 'shorturl': short_url, 'root': root, 'dir': path}
        url = 'https://www.terabox.com/share/list?' + '&'.join([f'{a}={b}' for a, b in params.items()])
        req = self.r.get(url, headers=self.headers, cookies={'cookie': ''}).json()
        return self.packData(req, short_url)

    def checkFileType(self, name):
        name = name.lower()
        if any(ext in name for ext in ['.mp4', '.mov', '.m4v', '.mkv', '.asf', '.avi', '.wmv', '.m2ts', '.3g2']):
            return 'video'
        elif any(ext in name for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']):
            return 'image'
        elif any(ext in name for ext in ['.pdf', '.docx', '.zip', '.rar', '.7z']):
            return 'file'
        else:
            return 'other'

class TeraboxLink:
    def __init__(self, fs_id, uk, shareid, timestamp, sign, js_token, cookie):
        self.r = requests.Session()
        self.headers = HEADERS
        self.result = {'status': 'failed', 'download_link': {}}
        self.cookie = cookie
        self.dynamic_params = {
            'uk': str(uk),
            'sign': str(sign),
            'shareid': str(shareid),
            'primaryid': str(shareid),
            'timestamp': str(timestamp),
            'jsToken': str(js_token),
            'fid_list': str(f'[{fs_id}]')
        }
        self.static_param = {
            'app_id': '250528',
            'channel': 'dubox',
            'product': 'share',
            'clienttype': '0',
            'dp-logid': '',
            'nozip': '0',
            'web': '1'
        }

    def generate(self):
        params = {**self.dynamic_params, **self.static_param}
        url = 'https://www.terabox.com/share/download?' + '&'.join([f'{a}={b}' for a, b in params.items()])
        req = self.r.get(url, cookies={'cookie': self.cookie}).json()

        if not req['errno']:
            slow_url = req['dlink']
            self.result['download_link'].update({'url_1': slow_url})
            self.result['status'] = 'success'
            self.generateFastURL()

        self.r.close()

    def generateFastURL(self):
        r = requests.Session()
        try:
            old_url = r.head(self.result['download_link']['url_1'], allow_redirects=True).url
            old_domain = re.search(r'://(.*?)\.', str(old_url)).group(1)
            medium_url = old_url.replace('by=themis', 'by=dapunta')
            fast_url = old_url.replace(old_domain, 'd3').replace('by=themis', 'by=dapunta')
            self.result['download_link'].update({'url_2': medium_url, 'url_3': fast_url})
        except:
            pass
        r.close()

@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a Terabox link, and I'll fetch the file list for you!")

@bot.on_message(filters.command("terabox"))
def handle_terabox(client, message):
    url = message.text.split(' ', 1)
    
    if len(url) < 2:
        message.reply_text("Please provide a Terabox URL after the command.")
        return

    url = url[1].strip()

    if "terabox" not in url:
        message.reply_text("Please send a valid Terabox link!")
        return

    message.reply_text("Fetching file details... ⏳")

    tf = TeraboxFile()
    tf.search(url)

    if tf.result['status'] == 'success':
        file_info = "**Files in this folder:**\n"
        for file in tf.result['list']:
            size = f"{file['size']} bytes" if file['size'] else "📁 Folder"
            file_info += f"📄 {file['name']} - {size}\n"

            # Add download link generation logic for files
            if file['type'] != 'other':  # Only files (not directories)
                fs_id = file['fs_id']
                uk = tf.result['uk']
                shareid = tf.result['shareid']
                timestamp = tf.result['timestamp']
                sign = tf.result['sign']
                js_token = tf.result['js_token']
                cookie = tf.result['cookie']
                
                # Generate download link
                terabox_link = TeraboxLink(fs_id, uk, shareid, timestamp, sign, js_token, cookie)
                terabox_link.generate()

                if terabox_link.result['status'] == 'success':
                    download_link = terabox_link.result['download_link']
                    file_info += f"🔗 Download: {download_link.get('url_3', 'No link available')}\n"
        
        message.reply_text(file_info)
    else:
        message.reply_text("Failed to fetch details. Please check the link!")

bot.run()
