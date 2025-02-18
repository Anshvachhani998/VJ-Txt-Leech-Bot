from pyrogram import Client, filters
from pyrogram.types import Message
import requests
import re
import logging
from vars import API_ID, API_HASH, BOT_TOKEN

# Initialize bot
bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.basicConfig(level=logging.INFO)

# Headers for Terabox requests
HEADERS = {
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36"
}

class TeraboxFile:
    def __init__(self):
        self.r = requests.Session()
        self.headers = HEADERS
        self.result = {
            'status': 'failed', 'js_token': '', 'browser_id': '', 'cookie': '',
            'sign': '', 'timestamp': '', 'shareid': '', 'uk': '', 'list': []
        }

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
        self.result.update({'js_token': js_token, 'browser_id': browser_id, 'cookie': cookie})

    def getMainFile(self):
        url = f'https://www.terabox.com/api/shorturlinfo?app_id=250528&shorturl=1{self.short_url}&root=1'
        req = self.r.get(url, headers=self.headers, cookies={'cookie': ''}).json()
        all_file = self.packData(req, self.short_url)
        if all_file:
            self.result.update({
                'sign': req['sign'], 'timestamp': req['timestamp'],
                'shareid': req['shareid'], 'uk': req['uk'], 'list': all_file, 'status': 'success'
            })

    def packData(self, req, short_url):
        return [{
            'is_dir': item['isdir'], 'path': item['path'], 'fs_id': item['fs_id'],
            'name': item['server_filename'],
            'type': self.checkFileType(item['server_filename']) if not item['isdir'] else 'other',
            'size': item.get('size', '') if not item['isdir'] else '',
            'image': item.get('thumbs', {}).get('url3', '') if not item['isdir'] else '',
            'list': self.getChildFile(short_url, item['path'], '0') if item['isdir'] else [],
        } for item in req.get('list', [])]

    def getChildFile(self, short_url, path='', root='0'):
        params = {'app_id': '250528', 'shorturl': short_url, 'root': root, 'dir': path}
        url = 'https://www.terabox.com/share/list?' + '&'.join([f'{a}={b}' for a, b in params.items()])
        req = self.r.get(url, headers=self.headers, cookies={'cookie': ''}).json()
        return self.packData(req, short_url)

    def checkFileType(self, name):
        name = name.lower()
        if any(ext in name for ext in ['.mp4', '.mkv', '.avi']):
            return 'video'
        elif any(ext in name for ext in ['.jpg', '.png', '.gif']):
            return 'image'
        elif any(ext in name for ext in ['.pdf', '.zip', '.rar']):
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
            'uk': str(uk), 'sign': str(sign), 'shareid': str(shareid),
            'primaryid': str(shareid), 'timestamp': str(timestamp),
            'jsToken': str(js_token), 'fid_list': f'[{fs_id}]'
        }
        self.static_param = {
            'app_id': '250528', 'channel': 'dubox',
            'product': 'share', 'clienttype': '0',
            'dp-logid': '', 'nozip': '0', 'web': '1'
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
            match = re.search(r'sign=([^&]+)', old_url)
            if not match:
                return

            old_sign = match.group(1)
            old_domain = re.search(r'://(.*?)\.', str(old_url)).group(1)

            fast_url = old_url.replace(old_domain, 'd3')
            new_req = r.get(fast_url, headers=self.headers, cookies={'cookie': self.cookie}, allow_redirects=True)
            new_url = new_req.url

            if 'sign=' in new_url:
                self.result['download_link'].update({'url_2': new_url})

        except Exception:
            pass
        r.close()

@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a Terabox link, and I'll fetch the file list for you!")

@bot.on_message(filters.command("terabox"))
def handle_terabox(client, message):
    url = message.text.split(' ', 1)[1].strip()
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

            if file['type'] != 'other':
                link = TeraboxLink(file['fs_id'], tf.result['uk'], tf.result['shareid'],
                                   tf.result['timestamp'], tf.result['sign'], tf.result['js_token'], tf.result['cookie'])
                link.generate()
                if link.result['status'] == 'success':
                    file_info += f"🔗 Download: {link.result['download_link'].get('url_1', 'No link')}\n"
                    file_info += f"⚡ Fast: {link.result['download_link'].get('url_2', 'No link')}\n"

        message.reply_text(file_info)
    else:
        message.reply_text("Failed to fetch details!")

bot.run()
