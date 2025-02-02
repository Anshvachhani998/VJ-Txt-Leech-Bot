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


# JioCinema Guest Token API
GUEST_TOKEN_URL = "https://auth-jiocinema.voot.com/tokenservice/apis/v4/guest"

# Headers for request
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)"
}

# Request Data
GUEST_DATA = {
    "appName": "RJIL_JioCinema",
    "deviceType": "fireTV",
    "os": "android",
    "deviceId": "1464251119",
    "freshLaunch": False,
    "adId": "1464251119",
    "appVersion": "4.1.3"
}

# Function to fetch guest token
def fetch_guest_token():
    """Fetch Guest Token from JioCinema Server."""
    try:
        response = requests.post(GUEST_TOKEN_URL, json=GUEST_DATA, headers=HEADERS)
        if response.status_code == 200:
            result = response.json()
            token = result.get("authToken")
            if token:
                return f"✅ **Guest Token:** `{token}`"
            else:
                return "❌ **Failed to Fetch Guest Token.**"
        else:
            return f"❌ **Error:** `{response.status_code} - {response.text}`"
    except Exception as e:
        return f"⚠ **Exception:** `{str(e)}`"

# Telegram command to get token
@bot.on_message(filters.command("gettoken") & filters.private)
def get_token(client, message):
    """Handle /gettoken command"""
    message.reply_text("🔄 **Fetching JioCinema Guest Token...**")
    token = fetch_guest_token()
    message.reply_text(token, parse_mode="markdown")
    

bot.run()
