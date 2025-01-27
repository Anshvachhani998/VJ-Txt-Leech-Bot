import os
from pyrogram import Client, filters
from spotdl import Spotdl

bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)

# Spotify credentials (replace with your actual client_id and client_secret)
client_id = 'feef7905dd374fd58ba72e08c0d77e70'
client_secret = '60b4007a8b184727829670e2e0f911ca'

# Initialize Spotdl with your credentials
spotify_downloader = Spotdl(client_id=client_id, client_secret=client_secret)

# Function to download song and send it to the user
def download_and_send_song(track_url, user_id):
    try:
        # Get track name from the URL
        track_name = spotify_downloader.get_track_name(track_url)
        
        # Download the song using spotdl
        file_path = f"downloads/{track_name}.mp3"
        spotify_downloader.download(track_url, file_path)
        
        # Check if file exists and send it to user
        if os.path.exists(file_path):
            with open(file_path, 'rb') as song_file:
                bot.send_audio(user_id, song_file)
            
            # Optionally, delete the file after sending
            os.remove(file_path)
        else:
            bot.send_message(user_id, "There was an issue downloading the song.")
    except Exception as e:
        bot.send_message(user_id, f"Error: {str(e)}")

# Command handler for !dwn <spotify_link>
@bot.on_message(filters.command("dwn"))
async def handle_download_command(client, message):
    # Extract the Spotify link after the command
    if len(message.text.split()) > 1:
        track_url = message.text.split()[1]
        await message.reply("Processing your request...")
        
        # Call the function to download and send the song
        download_and_send_song(track_url, message.chat.id)
    else:
        await message.reply("Please provide a valid Spotify link with the command. Example: !dwn <spotify_link>")

# Start command to greet the user
@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<b>Hello {m.from_user.mention} 👋\n\nI am a Spotify downloader bot. Use the command `/dwn <spotify_link>` to download your favorite songs from Spotify.</b>")

bot.run()
