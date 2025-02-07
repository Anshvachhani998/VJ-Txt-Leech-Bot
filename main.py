import requests
from pyrogram import Client, filters
from vars import API_ID, API_HASH, BOT_TOKEN
import time
import asyncio
from pymongo import MongoClient
from rapidfuzz import process, fuzz
from tqdm import tqdm
from pyrogram import Client, filters

bot = Client("MovieBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# --- MongoDB Configuration ---
MONGO_URI = "mongodb+srv://Ansh089:Ansh089@cluster0.y8tpouc.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "Web-Auto-files"
COLLECTION_NAME = "Web files 1"

def fetch_file_names():
    """Fetch all file names from MongoDB."""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    print("Fetching file names from MongoDB...")
    start_time = time.time()
    
    file_names = [doc["file_name"] for doc in collection.find({}, {"file_name": 1})]
    
    print(f"Fetched {len(file_names)} files in {time.time() - start_time:.2f} seconds.")
    return file_names

def group_similar_movies(file_names, threshold=80):
    """Group similar movies based on fuzzy matching."""
    groups = {}
    
    print("Processing files for similarity matching...")
    for file in tqdm(file_names, desc="Matching"):
        match = process.extractOne(file, groups.keys(), scorer=fuzz.partial_ratio)
        if match and match[1] > threshold:
            groups[match[0]].append(file)
        else:
            groups[file] = [file]
    
    return groups

@bot.on_message(filters.command("fetch"))
async def fetch_movies(client, message):
    """Handle the /fetch command."""
    await message.reply_text("🔍 Fetching movie data from database... Please wait.")

    file_names = fetch_file_names()
    if not file_names:
        await message.reply_text("⚠️ No files found in the database.")
        return
    
    start_time = time.time()
    similar_movie_groups = group_similar_movies(file_names)

    response = "**📊 Movie Analysis Report**\n"
    for movie, variations in similar_movie_groups.items():
        response += f"🎬 **{movie}** - `{len(variations)}` Variations\n"

    response += f"\n✅ **Total Unique Movie Names:** `{len(similar_movie_groups)}`"
    response += f"\n⏳ **Processing Time:** `{time.time() - start_time:.2f} sec`"

    # Sending results in chunks if message is too long
    if len(response) > 4096:
        for chunk in [response[i:i+4000] for i in range(0, len(response), 4000)]:
            await message.reply_text(chunk)
    else:
        await message.reply_text(response)

# --- Run the bot ---
print("🤖 Bot is running...")
bot.run()
