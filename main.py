import os
import requests
import subprocess
import time
import asyncio
import re
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

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
    url = "https://www.jiocinema.com/movies"  # Sample API endpoint

    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            await message.reply("✅ Cookies are valid! You are authenticated.")
        else:
            await message.reply(f"⚠️ Invalid cookies! Status Code: {response.status_code}")
    except Exception as e:
        await message.reply(f"❌ Error checking cookies: {str(e)}")

# Movie Info Command
@bot.on_message(filters.command("movie_info"))
async def fetch_movie_info(client, message):
    try:
        video_url = message.text.split(" ")[1]

        cookies = load_cookies()
        if not cookies:
            await message.reply("⚠️ Cookies file is missing or invalid.")
            return

        headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        
        response = requests.get(video_url, headers=headers, cookies=cookies)

        if response.status_code == 200:
            # Parse HTML content using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title, description, and other details (customize as per your requirement)
            title = soup.find('meta', {'property': 'og:title'})['content'] if soup.find('meta', {'property': 'og:title'}) else "Unknown Title"
            description = soup.find('meta', {'name': 'description'})['content'] if soup.find('meta', {'name': 'description'}) else "No description available."
            
            await message.reply(f"🎬 **Movie Info:**\n\n📌 Title: {title}\n📝 Description: {description}")
        else:
            await message.reply(f"⚠️ Failed to fetch movie details! Status Code: {response.status_code}")
    except IndexError:
        await message.reply("Usage: `/movie_info <movie_url>`")
    except Exception as e:
        await message.reply(f"❌ Error fetching movie details: {str(e)}")

# 🧩 Function to get video URL using Playwright Async API
async def get_video_url(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)
        
        # Extract video URL (customize based on the page structure)
        video_url = await page.evaluate("document.querySelector('video').src")
        
        await browser.close()
        
        return video_url

# 📥 Function to download video and show progress
async def download_video_func(url, message):
    # Get the video URL using Playwright
    video_url = await get_video_url(url)
    
    if not video_url:
        raise Exception("❌ Failed to extract video URL.")
    
    output_path = os.path.join(VIDEO_DIR, "output.mp4")
    print(f"Downloading video to: {output_path}")  # Debug log

    command = [
        "yt-dlp",
        "--cookies", COOKIES_PATH,  # Ensure the cookies are in Netscape format
        "--socket-timeout", "30",
        "-o", output_path,
        video_url
    ]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Function to read and parse the progress
    def read_progress():
        while True:
            stdout_line = process.stdout.readline()
            if stdout_line == '' and process.poll() is not None:
                break
            if stdout_line:
                # Check for progress info in the output and print it
                match = re.search(r'(\d+(\.\d{1,2})?)%\s*\[.*\]\s*(\d+(\.\d{1,2})?)s / (\d+(\.\d{1,2})?)', stdout_line)
                if match:
                    progress_percentage = match.group(1)
                    eta_time = match.group(5)
                    print(f"Progress: {progress_percentage}% | ETA: {eta_time}s")
                    # Send this information to the user
                    yield progress_percentage, eta_time
                else:
                    print(stdout_line.strip(), end='')

    # Create a generator that yields progress updates
    progress_generator = read_progress()

    # Sending progress updates to the user
    async def send_progress_updates():
        for progress_percentage, eta_time in progress_generator:
            await message.reply(f"📥 Downloading... {progress_percentage}% completed. ETA: {eta_time}s")

    # Start the progress update loop asynchronously
    asyncio.create_task(send_progress_updates())

    stderr_output = process.stderr.read().decode()
    if stderr_output:
        print(f"❌ Error output: {stderr_output}")
        raise Exception(f"❌ Video download failed: {stderr_output}")

    process.stdout.close()
    process.stderr.close()
    process.wait()

    if os.path.exists(output_path):
        return output_path
    else:
        raise Exception("❌ Video download failed.")

# 🧩 Bot handler for download command
@bot.on_message(filters.command("dwn"))
async def download_video(client, message):
    try:
        # Check if a URL is provided in the command
        if len(message.text.split(" ")) < 2:
            await message.reply("❌ Usage: `/dwn <JioCinema URL>`")
            return

        video_url = message.text.split(" ")[1]
        await message.reply(f"📥 Processing your link: {video_url}")

        # Call the function to download the video (ensure it's async)
        video_path = await download_video_func(video_url, message)

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

bot.run()
