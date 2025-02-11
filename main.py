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

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

session = requests.Session()

# Common Headers for JioCinema API
headers = {
    "Origin": "https://www.jiocinema.com",
    "Referer": "https://www.jiocinema.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
}

# Function to Fetch Guest Token using Session
def fetch_guest_token():
    url = "https://auth-jiocinema.voot.com/tokenservice/apis/v4/guest"
    data = {
        "appName": "RJIL_JioCinema",
        "deviceType": "fireTV",
        "os": "android",
        "deviceId": "1464251119",
        "freshLaunch": False,
        "adId": "1464251119",
        "appVersion": "4.1.3"
    }

    try:
        response = session.post(url, json=data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result.get("authToken", "❌ Token Not Found")
        return "❌ Request Failed"
    except requests.RequestException as e:
        return f"❌ Error: {e}"

# Telegram Command to Get Guest Token
@bot.on_message(filters.command("gettoken"))
async def send_token(client, message):
    await message.reply_text("🔄 Fetching JioCinema Guest Token...")
    token = fetch_guest_token()
    await message.reply_text(f"✅ **Guest Token:**\n`{token}`")



print("🤖 Bot is running...")
bot.run()
