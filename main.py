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

MONGO_URI = "mongodb+srv://Ansh089:Ansh089@cluster0.y8tpouc.mongodb.net/?retryWrites=true&w=majority"
DB_NAME = "Web-Auto-files"
COLLECTION_NAME = "Web files 1"

def fetch_file_names(limit=5000):
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]
    
    start_time = time.time()
    file_names = [doc["file_name"] for doc in collection.find({}, {"file_name": 1}).limit(limit)]
    print(f"Fetched {len(file_names)} files in {time.time() - start_time:.2f} seconds.")
    return file_names

def clean_file_name(file_name):
    # Step 1: Handle season/episode pattern and year
    # Retain s01e01, s01, season 1 etc. and remove extra terms after year
    file_name = re.sub(r"(\b(s\d{1,2}e\d{1,2}|\bs\d{1,2}|\bseason \d{1,2})\b)", r"\1", file_name)

    # Step 2: Remove extra words after the year
    file_name = re.sub(r"(\d{4})(.*)", r"\1", file_name)  # Keep only the year part
    
    # Step 3: Remove known extra words like 1080p, mkv, hd, etc.
    extra_words = ['1080p', '720p', '480p', 'web-dl', 'x264', 'mkv', 'avi', 'mp4', 'hdrip', 'webrip', 'bluRay', 'camrip', 'xvid', 'aac', 'dvdrip', 'brrip', 'sub', 'hq', 'hd', 'english', 'hindi', 'tamil', 'telugu', 'dubbed', 'full movie', 'official', 'complete', 'unrated', 'dual audio']
    for word in extra_words:
        file_name = file_name.replace(word, "")

    # Step 4: Remove extra spaces after cleaning
    file_name = re.sub(r'\s+', ' ', file_name).strip()

    return file_name

def process_file_chunk(chunk, existing_keys, threshold=80):
    """Parallel processing function"""
    local_groups = {}
    for file in chunk:
        match = process.extractOne(file, existing_keys, scorer=fuzz.partial_ratio)
        if match and match[1] > threshold:
            local_groups[match[0]].append(file)
        else:
            local_groups[file] = [file]
    return local_groups

def group_similar_movies_parallel(file_names, threshold=80, num_threads=8):
    """Multi-threaded fuzzy matching"""
    chunk_size = len(file_names) // num_threads
    chunks = [file_names[i:i + chunk_size] for i in range(0, len(file_names), chunk_size)]

    groups = {}
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = list(tqdm(executor.map(process_file_chunk, chunks, [groups.keys()] * len(chunks)), total=len(chunks), desc="Matching"))

    for result in results:
        groups.update(result)

    return groups

def save_to_file(file_data, filename="movie_groups.txt"):
    """Save large results to a text file."""
    with open(filename, "w") as file:
        file.write(file_data)

@bot.on_message(filters.command("fetch"))
async def fetch_movies(client, message):
    args = message.text.split()
    limit = int(args[1]) if len(args) > 1 and args[1].isdigit() else 5000
    
    await message.reply_text(f"🔍 Fetching `{limit}` movie records from the database... Please wait.")
    file_names = fetch_file_names(limit)
    if not file_names:
        await message.reply_text("⚠️ No files found in the database.")
        return
    
    start_time = time.time()
    
    # Clean file names
    cleaned_file_names = [clean_file_name(file) for file in file_names]
    
    # Group similar movies
    similar_movie_groups = group_similar_movies_parallel(cleaned_file_names)

    response = "**📊 Movie Analysis Report**\n"
    for movie, variations in similar_movie_groups.items():
        response += f"🎬 **{movie}** - `{len(variations)}` Variations\n"

    response += f"\n✅ **Total Unique Movie Names:** `{len(similar_movie_groups)}`"
    response += f"\n⏳ **Processing Time:** `{time.time() - start_time:.2f} sec`"

    # If response exceeds 4096 chars, split into multiple messages
    if len(response) > 4096:
        # Save to file
        save_to_file(response)
        await message.reply_text("The result is too large to display here. I have saved the results in a file.")
        await message.reply_document("movie_groups.txt")
    else:
        await message.reply_text(response)

print("🤖 Bot is running...")
bot.run()
