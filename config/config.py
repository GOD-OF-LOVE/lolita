import os
import re
import sys
import typing

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

# bot version
__lolitha_version__ = "0.0.0"

# get it from my.telegram.org
API_ID = int(os.getenv("API_ID", ""))
API_HASH = os.getenv("API_HASH")

# get it token bot from @BotFather in telegram.
TELEGRAM = os.getenv("TELEGRAM")

# database to save your chats and stats. Get MongoDB:-  https://telegra.ph/How-To-get-Mongodb-URI-04-06
MongoDatabaseURI = os.getenv("MongoDatabaseURI")

# the developer account id
DeveloperID = list(map(int, os.getenv("DeveloperID", "").split()))

log_chat = int(os.getenv("log_chat", None))
prefixes: typing.List[str] = ["/", "!", ".", "$", "-"]
banned_users = filters.user()
downloader = 1
log_file_name = "lolithalogs.txt"

# the duration limit 
DurationLimit = os.getenv("DurationLimit", "60")

# string session
SessionString = os.getenv("SessionString", None)
SessionString2 = os.getenv("SessionString2", None)

# set it in True if you want to leave your assistant after a certain amount of time.
ClientAutoLeave = os.getenv("ClientAutoLeave", None)

# time after which you're assistant account will leave chats automatically.
TimerAutoLeave = int(
    os.getenv("TimerAutoLeave", "5400")
)

# set it True if you want to delete downloads after the music playout ends from your downloads folder
AUTO_DOWNLOADS_CLEAR = os.getenv("AUTO_DOWNLOADS_CLEAR", None)

# time sleep duration For Youtube downloader
YOUTUBE_DOWNLOAD_EDIT_SLEEP = int(os.getenv("YOUTUBE_EDIT_SLEEP", "3"))

# time sleep duration for telegram downloader
TELEGRAM_DOWNLOAD_EDIT_SLEEP = int(os.getenv("TELEGRAM_EDIT_SLEEP", "5"))

YouTubeThumbnail = "cache/youtube.jpg"

def time_to_seconds(time):
    stringt = str(time)
    return sum(
        int(x) * 60**i
        for i, x in enumerate(reversed(stringt.split(":")))
    )

duration_limit = int(time_to_seconds(f"{DurationLimit}:00"))
