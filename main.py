import requests
from pyrogram import Client, filters
from vars import API_ID, API_HASH, BOT_TOKEN

# Initialize the bot
bot = Client("JioCinemaBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# JioCinema Guest Token API
GUEST_TOKEN_URL = "https://auth-jiocinema.voot.com/tokenservice/apis/v4/guest"

# Headers & Request Data
HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10)"
}

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
                return f"Guest Token: {token}"
            else:
                return "Failed to Fetch Guest Token."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

# Handle /gettoken command
@bot.on_message(filters.command("gettoken") & filters.private)
def get_token(client, message):
    """Handle /gettoken command"""
    message.reply_text("Fetching JioCinema Guest Token...")

    token = fetch_guest_token()
    
    message.reply_text(token)  # No parse_mode used (plain text only)

# Run the bot
bot.run()
