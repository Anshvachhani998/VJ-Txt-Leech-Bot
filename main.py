import os
import requests
import subprocess
import time
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen

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

# ✅ Command to check if cookies are valid
@bot.on_message(filters.command("check_cookies"))
async def check_cookies(client, message):
    cookies = load_cookies()
    if not cookies:
        await message.reply("⚠️ Cookies file is empty or invalid.")
        return

    headers = {"User-Agent": "Mozilla/5.0"}
    url = "https://www.jiocinema.com/api/v1/movies"  # Sample API endpoint

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            await message.reply("✅ Cookies are valid! You are authenticated.")
        else:
            await message.reply(f"⚠️ Invalid cookies! Status Code: {response.status_code}")
    except Exception as e:
        await message.reply(f"❌ Error checking cookies: {str(e)}")

# 🎬 Command to fetch movie details
@bot.on_message(filters.command("movie_info"))
async def fetch_movie_info(client, message):
    try:
        video_url = message.text.split(" ")[1]
        movie_id = video_url.split("/")[-2]  # Extract movie ID from URL

        cookies = load_cookies()
        if not cookies:
            await message.reply("⚠️ Cookies file is missing or invalid.")
            return

        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        api_url = f"https://www.jiocinema.com/api/v1/movies/{movie_id}"

        response = requests.get(api_url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            data = response.json()
            title = data.get("title", "Unknown Title")
            description = data.get("description", "No description available.")
            duration = data.get("duration", "Unknown duration")

            await message.reply(f"🎬 **Movie Info:**\n\n📌 Title: {title}\n📝 Description: {description}\n⏳ Duration: {duration}")
        else:
            await message.reply(f"⚠️ Failed to fetch movie details! Status Code: {response.status_code}")
    except IndexError:
        await message.reply("Usage: `/movie_info <movie_url>`")
    except Exception as e:
        await message.reply(f"❌ Error fetching movie details: {str(e)}")

# ⬇️ Command to download video
@bot.on_message(filters.command("dwn"))
async def download_video(client, message):
    try:
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

    except IndexError:
        await message.reply("Usage: `/dwn <JioCinema URL>`")
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

# 📥 Function to download video
def download_video_func(url):
    output_path = os.path.join(VIDEO_DIR, "output.mp4")

    command = [
        "yt-dlp",
        "--cookies", COOKIES_PATH,
        "--socket-timeout", "30",
        "-f", "135",  # 360p quality
        "-o", output_path,
        url
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for stdout_line in iter(process.stdout.readline, b''):
        print(stdout_line.decode(), end='')

    stderr_output = process.stderr.read().decode()
    if stderr_output:
        print(f"❌ Error output: {stderr_output}")

    process.stdout.close()
    process.stderr.close()
    process.wait()

    if os.path.exists(output_path):
        return output_path
    else:
        raise Exception("❌ Video download failed.")

bot.run()
