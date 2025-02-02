import requests
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from vars import API_ID, API_HASH, BOT_TOKEN

# Initialize the bot
bot = Client("JioCinemaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Proxy Configuration
PROXIES = {
    "http": "http://103.140.142.201:32650",
    "https": "https://103.140.142.201:32650"
}

# Common Headers for Requests
HEADERS = {
    "Origin": "https://www.jiocinema.com",
    "Referer": "https://www.jiocinema.com/",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
}

# API URL for JioCinema Guest Token
GUEST_TOKEN_URL = "https://auth-jiocinema.voot.com/tokenservice/apis/v4/guest"

# API Request Data
GUEST_DATA = {
    "appName": "RJIL_JioCinema",
    "deviceType": "fireTV",
    "os": "android",
    "deviceId": "1464251119",
    "freshLaunch": False,
    "adId": "1464251119",
    "appVersion": "4.1.3"
}


# Function to Fetch JioCinema Guest Token
def fetch_guest_token():
    try:
        with requests.Session() as session:
            response = session.post(GUEST_TOKEN_URL, json=GUEST_DATA, headers=HEADERS, proxies=PROXIES)
            
            if response.status_code == 200:
                result = response.json()
                token = result.get("authToken")
                return token if token else "❌ Failed to fetch token"
            else:
                return f"❌ Error: {response.status_code} - {response.text}"
    
    except requests.exceptions.RequestException as e:
        return f"⚠ Exception: {str(e)}"


# 📌 Command 1: `/gettoken`
@bot.on_message(filters.command("gettoken") & filters.private)
def get_token(client, message):
    """Handle /gettoken command"""
    message.reply_text("🔄 Fetching JioCinema Guest Token...")

    token = fetch_guest_token()
    message.reply_text(f"✅ Guest Token:\n\n{token}")


# 📌 Command 2: `/getnewtoken`
@bot.on_message(filters.command("getnewtoken") & filters.private)
def get_new_token(client, message):
    """Handle /getnewtoken command"""
    message.reply_text("🔄 Generating a new JioCinema Guest Token...")

    token = fetch_guest_token()
    message.reply_text(f"🔹 New Guest Token:\n\n{token}")


# Run the bot
bot.run()
