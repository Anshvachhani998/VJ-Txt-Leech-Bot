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

@bot.on_message(filters.command(["start"]))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<b>Hello {m.from_user.mention} 👋\n\n I Am A Bot For Download Links From Your **.TXT** File And Then Upload That File On Telegram So Basically If You Want To Use Me First Send Me /upload Command And Then Follow Few Steps..\n\nUse /stop to stop any ongoing task.</b>")


      

bot.run()
