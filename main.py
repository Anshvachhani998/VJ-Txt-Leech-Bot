import requests
from pyrogram import Client, filters
from vars import API_ID, API_HASH, BOT_TOKEN

# Pyrogram bot client
bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Terabox API endpoint
TERABOX_API_URL = "https://teradl-api.dapuntaratya.com/generate_file"

# Required Headers
HEADERS = {
    "Content-Type": "application/json"
}

@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply("👋 Hello! Send me a Terabox URL using `/dl` command.\n\nExample:\n`/dl https://terabox.com/s/examplelink`")

@bot.on_message(filters.command("dl"))
def download_file(client, message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        message.reply("❌ Please provide a URL. Example:\n`/dl https://terabox.com/s/examplelink`")
        return

    url = args[1].strip()
    message.reply("🔄 Fetching file details, please wait...")

    try:
        # Terabox API Request
        payload = {"url": url}  # "mode" remove kar diya gaya hai
        response = requests.post(TERABOX_API_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            data = response.json()
            
            if data.get("status") == "success":
                file_name = data.get("name", "Unknown")
                file_size = data.get("size", "Unknown")
                thumbnail = data.get("image", None)

                reply_text = f"📂 **File Name:** `{file_name}`\n📦 **File Size:** `{file_size} MB`"
                message.reply(reply_text)

                # Agar thumbnail available hai toh send karein
                if thumbnail:
                    client.send_photo(message.chat.id, thumbnail, caption="🖼 File Thumbnail")
            else:
                message.reply("❌ Failed to retrieve file details. Please check the URL.")
        else:
            message.reply(f"⚠️ API Error {response.status_code}: Unable to fetch details.")
    
    except Exception as e:
        message.reply(f"⚠️ Error: {str(e)}")

# Bot run karne ka function
bot.run()
