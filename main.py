from pyrogram import Client, filters
from vars import API_ID, API_HASH, BOT_TOKEN

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

from requests import get, post
from urllib.parse import urlparse
import os

class DirectDownloadLinkException(Exception):
    pass

def terabox(url, video_quality="HD Video", save_dir="HD_Video"):
    """Terabox direct link generator"""

    if not ("/s/" in url or "surl=" in url):
        raise DirectDownloadLinkException("❌ Invalid Terabox URL")

    netloc = urlparse(url).netloc
    terabox_url = url.replace(netloc, "1024tera.com")

    urls = [
        "https://ytshorts.savetube.me/api/v1/terabox-downloader",
        f"https://teraboxvideodownloader.nepcoderdevs.workers.dev/?url={terabox_url}",
        f"https://terabox.udayscriptsx.workers.dev/?url={terabox_url}",
        f"https://mavimods.serv00.net/Mavialt.php?url={terabox_url}",
        f"https://mavimods.serv00.net/Mavitera.php?url={terabox_url}",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.5",
        "Content-Type": "application/json",
    }

    for base_url in urls:
        try:
            response = post(base_url, headers=headers, json={"url": terabox_url}) if "api/v1" in base_url else get(base_url)
            if response.status_code == 200:
                break
        except Exception as e:
            raise DirectDownloadLinkException(f"❌ Error: {e.__class__.__name__}") from e
    else:
        raise DirectDownloadLinkException("❌ Unable to fetch download link")

    data = response.json()
    details = {"contents": [], "title": "", "total_size": 0}

    for item in data.get("response", []):
        title = item["title"]
        resolutions = item.get("resolutions", {})
        if (zlink := resolutions.get(video_quality)):
            details["contents"].append({"url": zlink, "filename": title, "path": os.path.join(title, save_dir)})
        details["title"] = title

    if not details["contents"]:
        raise DirectDownloadLinkException("❌ No valid download links found")

    return details["contents"][0]["url"] if len(details["contents"]) == 1 else details

@bot.on_message(filters.command("terabox") & filters.text)
async def terabox_command(client, message):
    if len(message.command) < 2:
        await message.reply_text("⚠ Usage: /terabox <terabox_url>")
        return

    url = message.command[1]
    await message.reply_text("🔄 Fetching download link...")

    try:
        download_link = terabox(url)
        if isinstance(download_link, dict):
            response_text = f"🎥 **{download_link['title']}**\n\n"
            for item in download_link["contents"]:
                response_text += f"🔹 **{item['filename']}**\n🔗 {item['url']}\n\n"
            await message.reply_text(response_text)
        else:
            await message.reply_text(f"✅ **Download Link:**\n{download_link}")
    except Exception as e:
        await message.reply_text(str(e))


bot.run()
