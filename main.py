from pyrogram import Client, filters
from pyrogram.types import Message
from requests import Session
from urllib.parse import urlparse, parse_qs
from re import findall
import os
import requests


# Bot Credentials
from vars import API_ID, API_HASH, BOT_TOKEN, COOKIE

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

from urllib.parse import parse_qs, urlparse


def check_url_patterns(url):
    patterns = [
        r"ww\.mirrobox\.com", r"www\.nephobox\.com", r"freeterabox\.com",
        r"www\.freeterabox\.com", r"1024tera\.com", r"4funbox\.co",
        r"www\.4funbox\.com", r"mirrobox\.com", r"nephobox\.com",
        r"terabox\.app", r"terabox\.com", r"www\.terabox\.ap",
        r"www\.terabox\.com", r"www\.1024tera\.co", r"www\.momerybox\.com",
        r"teraboxapp\.com", r"momerybox\.com", r"tibibox\.com",
        r"www\.tibibox\.com", r"www\.teraboxapp\.com"
    ]
    return any(re.search(pattern, url) for pattern in patterns)

def get_urls_from_string(string: str) -> list[str]:
    pattern = r"(https?://\S+)"
    urls = re.findall(pattern, string)
    return [url for url in urls if check_url_patterns(url)] or []

def find_between(data: str, first: str, last: str) -> str | None:
    try:
        start = data.index(first) + len(first)
        end = data.index(last, start)
        return data[start:end]
    except ValueError:
        return None

def extract_surl_from_url(url: str) -> str | None:
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    return query_params.get("surl", [None])[0]

def get_data(url: str):
    r = requests.Session()
    headersList = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9,hi;q=0.8",
        "Connection": "keep-alive",
        "Cookie": COOKIE,
        "DNT": "1",
        "Host": "www.terabox.app",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
    }
    
    response = r.get(url, headers=headersList)
    response = r.get(response.url, headers=headersList)
    logid = find_between(response.text, "dp-logid=", "&")
    jsToken = find_between(response.text, "fn%28%22", "%22%29")
    bdstoken = find_between(response.text, 'bdstoken":"', '"')
    shorturl = extract_surl_from_url(response.url)
    if not shorturl:
        return False
    
    reqUrl = f"https://www.terabox.app/share/list?app_id=250528&web=1&channel=0&jsToken={jsToken}&dp-logid={logid}&page=1&num=20&by=name&order=asc&site_referer=&shorturl={shorturl}&root=1"
    response = r.get(reqUrl, headers=headersList)
    
    if response.status_code != 200:
        return False
    
    r_j = response.json()
    if r_j.get("errno") or not r_j.get("list"):
        return False
    
    file_data = r_j["list"][0]
    direct_link = r.head(file_data["dlink"], headers=headersList).headers.get("location")
    
    return {
        "file_name": file_data["server_filename"],
        "link": file_data["dlink"],
        "direct_link": direct_link,
        "thumb": file_data["thumbs"]["url3"],
        "size": int(file_data["size"]),
        "sizebytes": int(file_data["size"])
    }


@bot.on_message(filters.command("terabox") & filters.private)
def terabox_handler(client, message):
    if len(message.command) < 2:
        message.reply_text("Please provide a TeraBox link.")
        return
    
    url = message.command[1]
    data = get_data(url)
    
    if not data:
        message.reply_text("Invalid or unsupported TeraBox link.")
        return
    
    reply_text = (
        f"📂 **File Name:** {data['file_name']}\n"
        f"📦 **Size:** {data['size']}\n"
        f"🔗 [Download Link]({data['link']})\n"
        f"🚀 [Direct Link]({data['direct_link']})"
    )
    
    message.reply_text(reply_text, disable_web_page_preview=True)




bot.run()
