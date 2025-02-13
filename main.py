import requests
from pyrogram import Client, filters
from vars import API_ID, API_HASH, BOT_TOKEN

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

TERABOX_FILE_URL = "https://teradl-api.dapuntaratya.com/generate_file"
TERABOX_LINK_URL = "https://teradl-api.dapuntaratya.com/generate_link"

HEADERS = {
    "Content-Type": "application/json"
}

@bot.on_message(filters.command("start"))
def start(client, message):
    message.reply("👋 Send me a Terabox URL using `/dl` command.\n\nExample:\n`/dl https://terabox.com/s/examplelink`")

@bot.on_message(filters.command("dl"))
def download_file(client, message):
    args = message.text.split(maxsplit=1)
    
    if len(args) < 2:
        message.reply("❌ Please provide a URL. Example:\n`/dl https://terabox.com/s/examplelink`")
        return

    url = args[1].strip()
    message.reply("🔄 Fetching file details, please wait...")

    try:
        payload = {"url": url}
        response = requests.post(TERABOX_FILE_URL, headers=HEADERS, json=payload)

        if response.status_code == 200:
            data = response.json()

            if data.get("status") == "success":
                file_list = data.get("list", [])

                if file_list and isinstance(file_list, list):
                    file_info = file_list[0]  # Pehli file ka data

                    file_name = file_info.get("name", "Unknown")
                    file_size = file_info.get("size", "Unknown")
                    thumbnail = file_info.get("image", None)

                    # Convert file size to MB
                    try:
                        file_size_mb = round(int(file_size) / (1024 * 1024), 2)
                    except:
                        file_size_mb = "Unknown"

                    message.reply(f"📂 **File Name:** `{file_name}`\n📦 **File Size:** `{file_size_mb} MB`\n⏳ Generating Download Link...")

                    # Generate Download Link Payload
                    download_payload = {
                        "js_token": data.get("js_token"),
                        "cookie": data.get("cookie"),
                        "sign": data.get("sign"),
                        "timestamp": data.get("timestamp"),
                        "shareid": data.get("shareid"),
                        "uk": data.get("uk"),
                        "fs_id": file_info.get("fs_id")
                    }
                    link_response = requests.post(TERABOX_LINK_URL, headers=HEADERS, json=download_payload)

                    if link_response.status_code == 200:
                        link_data = link_response.json()

                        if link_data.get("status") == "success":
                            download_link = link_data.get("download_link", {}).get("url_1", "No link found")
                            message.reply(f"✅ **Download Link:** [Click Here]({download_link})")
                        else:
                            message.reply("❌ Failed to generate the download link.")
                    else:
                        message.reply(f"⚠️ API Error {link_response.status_code}: Unable to generate link.")

                    if thumbnail:
                        client.send_photo(message.chat.id, thumbnail, caption="🖼 File Thumbnail")
                else:
                    message.reply("❌ No files found in the provided URL.")
            else:
                message.reply("❌ Failed to retrieve file details. Please check the URL.")
        else:
            message.reply(f"⚠️ API Error {response.status_code}: Unable to fetch details.")

    except Exception as e:
        message.reply(f"⚠️ Error: {str(e)}")

bot.run()
