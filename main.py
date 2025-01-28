import os
import requests
import subprocess
import time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
import yt_dlp as youtube_dl
from vars import API_ID, API_HASH, BOT_TOKEN
# Initialize the bot with your API keys
bot = Client("JioCinemaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

COOKIES_PATH = os.getenv("COOKIES_PATH", "cookies.txt")
VIDEO_DIR = "videos"
os.makedirs(VIDEO_DIR, exist_ok=True)  # Ensure videos folder exists

# Function to load cookies from file
def load_cookies():
    cookies = {}
    if os.path.exists(COOKIES_PATH):
        with open(COOKIES_PATH, "r") as file:
            for line in file:
                if not line.startswith("#") and line.strip():
                    parts = line.split("\t")
                    if len(parts) >= 7:
                        cookies[parts[5]] = parts[6].strip()
    return cookies

@bot.on_message(filters.command("check_cookies"))
async def check_cookies(client, message):
    cookies = load_cookies()
    if not cookies:
        await message.reply("⚠️ Cookies file is empty or invalid.")
        return

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.jiocinema.com/movies"  # Sample API endpoint

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            await message.reply("✅ Cookies are valid! You are authenticated.")
        else:
            await message.reply(f"⚠️ Invalid cookies! Status Code: {response.status_code}")
    except Exception as e:
        await message.reply(f"❌ Error checking cookies: {str(e)}")

@bot.on_message(filters.command("dwn"))
async def download_video(client, message):
    try:
        # Check if a URL is provided in the command
        if len(message.text.split(" ")) < 2:
            await message.reply("❌ Usage: `/dwn <video_url>`")
            return

        video_url = message.text.split(" ")[1]
        await message.reply(f"📥 Processing your link: {video_url}")

        video_path = download_video_func(video_url)

        if os.path.exists(video_path):
            await message.reply("✅ Download complete! Sending the video...")
            try:
                await bot.send_video(message.chat.id, video_path)
            except FloodWait as e:
                await message.reply(f"⚠️ Rate limit exceeded. Waiting for {e.x} seconds.")
                time.sleep(e.x)
                await bot.send_video(message.chat.id, video_path)
        else:
            await message.reply("❌ Error: The video could not be downloaded.")

    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# 📥 Function to download video using yt-dlp
def download_video_func(url):
    output_path = os.path.join(VIDEO_DIR, "output.mp4")
    print(f"Downloading video to: {output_path}")  # Debug log

    ydl_opts = {
        'outtmpl': output_path,
        'quiet': False,  # Show output for debugging
        'noplaylist': True,  # Avoid playlist downloads
        'extractaudio': False,
        'format': 'bestvideo+bestaudio/best',
        'cookies': COOKIES_PATH,
    }

    # Ensure yt-dlp handles the URL correctly
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])  # Download using yt-dlp
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise Exception(f"❌ Video download failed: {str(e)}")

    # Check if video downloaded successfully
    if os.path.exists(output_path):
        return output_path
    else:
        raise Exception("❌ Video download failed.")

bot.run()
