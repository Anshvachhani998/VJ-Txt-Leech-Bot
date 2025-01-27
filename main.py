import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess

import os
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait

import core as helper
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN
from aiohttp import ClientSession
from pyromod import listen
from subprocess import getstatusoutput

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


bot = Client(
    "bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN)


video_directory = "videos"



# Command to start the bot
@bot.on_message(filters.command("start"))
async def send_welcome(client, message):
    await message.reply("Welcome! Use /dwn <link> to download JioCinema videos.")

# Command to download video
@bot.on_message(filters.command("dwn"))
async def download_video(client, message):
    try:
        # Extracting the link from the message
        video_url = message.text.split(" ")[1]
        await message.reply(f"Processing your link: {video_url}")

        # Call the function to download video
        video_path = download_video_func(video_url)

        # Notify the user and send the downloaded video
        await message.reply("Download complete! Sending the video...")
        await bot.send_video(message.chat.id, video_path)
    except IndexError:
        await message.reply("Please provide a valid link! Usage: /dwn <link>")
    except Exception as e:
        await message.reply(f"Error: {str(e)}")



def download_video_func(url):
    cookies_path = os.getenv("COOKIES_PATH", "cookies.txt")  # Default to "cookies.txt" if not set
    output_path = "output.mp4"
    
    # Run yt-dlp command with progress info
    command = [
        "yt-dlp",
        "--cookies", cookies_path,
        "--socket-timeout", "30",
        "--progress",               # Show progress info in the console
        "-f", "135",                 # Format for lower quality (e.g., 360p)
        "-o", output_path,          # Output file name
        url                          # The video URL provided by the user
    ]
    
    # Run the command and capture the output
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Print progress info
    for stdout_line in iter(process.stdout.readline, b''):
        print(stdout_line.decode(), end='')  # Decode byte to string and print

    # Wait for the process to complete
    process.stdout.close()
    process.wait()

    return output_path  # Return the path of the downloaded video



bot.run()
