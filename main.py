import time
import asyncio
from pymongo import MongoClient
from rapidfuzz import process, fuzz
from tqdm import tqdm
from pyrogram import Client, filters
from concurrent.futures import ThreadPoolExecutor
from vars import API_ID, API_HASH, BOT_TOKEN
import re
import os
import requests

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

session = requests.Session()



# SonyLIV API Headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Referer": "https://www.sonyliv.com/",
    "Origin": "https://www.sonyliv.com"
}



def fetch_sonyliv_guest_token():
    url = "https://api.sonyliv.com/edge/v1/authorization/token"
    data = {
        "client_id": "sonyliv",
        "device_id": "guest_124637890",
        "device_platform": "web",
        "grant_type": "client_credentials"
    }

    retries = 3
    for attempt in range(retries):
        try:
            response = session.post(url, json=data, headers=headers, timeout=10)
            if response.status_code == 200:
                result = response.json()
                auth_token = result.get("access_token", "❌ Token Not Found")
                return auth_token
            else:
                return f"❌ Error: {response.status_code}"
        except requests.RequestException as e:
            if attempt < retries - 1:
                time.sleep(5)  # Wait before retrying
                continue
            return f"❌ Error: {e}"

    return "❌ Request Failed"


# Telegram Command to Get SonyLIV Guest Token
@bot.on_message(filters.command("sonyguesttoken"))
async def send_token(client, message):
    await message.reply_text("🔄 Fetching SonyLIV Guest Token...")
    token = fetch_sonyliv_guest_token()
    await message.reply_text(f"✅ **SonyLIV Guest Token:**\n`{token}`")


print("🤖 Bot is running...")
bot.run()
