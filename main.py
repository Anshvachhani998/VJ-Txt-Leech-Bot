import requests
from pyrogram import Client, filters
from vars import API_ID, API_HASH, BOT_TOKEN

# ✅ Initialize the bot
bot = Client("JioCinemaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ✅ Common Headers for Requests
HEADERS = {
    "Origin": "https://www.jiocinema.com",
    "Referer": "https://www.jiocinema.com/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; RMX2193) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "auth-jiocinema.voot.com",
    "Content-Type": "application/json"
}


# ✅ API URL for JioCinema Guest Token
GUEST_TOKEN_URL = "http://auth-jiocinema.voot.com/tokenservice/apis/v4/guest"

# ✅ API Request Data
# ✅ API Request Data (Updated)
GUEST_DATA = {
    "appName": "RJIL_JioCinema",
    "deviceType": "mobile",
    "os": "android",
    "deviceId": "d495f13c-ebb0-4778-8a31-3ccb9e873ca0",
    "adId": "d495f13c-ebb0-4778-8a31-3ccb9e873ca0",
    "appVersion": "25.01.13.1-b041218f"
}


# ✅ Function to Fetch JioCinema Guest Token (Proxy ke bina)
def fetch_guest_token():
    try:
        response = requests.post(GUEST_TOKEN_URL, json=GUEST_DATA, headers=HEADERS)  # ❌ proxies hata diya

        if response.status_code == 200:
            result = response.json()
            token = result.get("authToken")
            return token if token else "❌ Failed to fetch token"
        else:
            return f"❌ Error: {response.status_code} - {response.text}"
    
    except requests.exceptions.RequestException as e:
        return f"⚠ Exception: {str(e)}"

import os

# ✅ Command: `/gettoken`
@bot.on_message(filters.command("gettoken") & filters.private)
def get_token(client, message):
    """Handle /gettoken command"""
    message.reply_text("🔄 Fetching JioCinema Guest Token...")

    token = fetch_guest_token()

    if len(token) > 4000:
        file_path = "guest_token.txt"
        with open(file_path, "w") as file:
            file.write(token)  # Token ko file me save karo
        
        message.reply_document(file_path)  # File send karo
        os.remove(file_path)  # File delete kar do (temporary rakho)
    else:
        message.reply_text(f"✅ Guest Token:\n\n{token}")

# ✅ Command: `/getnewtoken`
@bot.on_message(filters.command("getnewtoken") & filters.private)
def get_new_token(client, message):
    """Handle /getnewtoken command"""
    message.reply_text("🔄 Generating a new JioCinema Guest Token...")

    token = fetch_guest_token()
    message.reply_text(f"🔹 New Guest Token:\n\n{token}")

# ✅ Run the bot
bot.run()
