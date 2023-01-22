import os
import time
import asyncio

from typing import Union
from pyrogram import types
from datetime import datetime, timedelta

import config
from lolithabot import self as lolitha, log
from lolithabot.helpers.formatter import convert_bytes, seconds_to_min
                                
xx = {}
downloader = {}


class TelegramDownload:
    def __init__(self):
        self.sleep = 5
        self.chars_limit = 4096
  
    async def send_split_text(self, message: types.Message, string):
        n = self.chars_limit
        out = [(string[i : i + n]) for i in range(0, len(string), n)]
        j = 0
        for x in out:
            if j <= 2:
                j += 1
                await message.reply_text(x)

        return True 

    async def get_link(self, message: types.Message):
        if message.chat.username:
            link = f"https://t.me/{message.chat.username}/{message.reply_to_message.message_id}"
        else:
            xf = str((message.chat.id))[4:]
            link = f"https://t.me/c/{xf}/{message.reply_to_message.message_id}"

        return link

    async def get_filename(
        self, file, audio: Union[bool, str] = None
    ):
        try:
            file_name = file.file_name
            if file_name is None:  
                file_name = (
                    "Audio file."
                    if audio
                    else "Video file." 
                )
            else:
                file_name = file.title if audio else "Video file."
        except:
            file_name = "Audio file." if audio else "Video file."

        return file_name

    async def get_duration(self, file):
        try:
            duration = second_to_min(file.duration)
        except:
            duration = "None"

        return duration

    async def get_filepath(
        self,
        audio: Union[bool, str] = None,
        video: Union[bool, str] = None
    ):
        if audio:
            try:
                file_name = (
                    audio.file_unique_id + "."
                    + (
                          (audio.file_name.split(".")[-1])
                          if not (isintante(audio, types.Voice))
                          else "ogg"
                    )
                )
            except:
                file_name = audio.file_unique_id + "." + ".ogg"

            file_name = os.path.join(
                os.path.realpath("downloads"), file_name
            )

        if video:
            try:
                file_name = (
                    video.file_unique_id
                    + "."
                    + (video.file_name.split(".")[-1])
                )
            except:
                file_name = video.file_unique_id + "." + "mp4"
       
            file_name = os.path.join(os.path.realpath("downloads"), file_name)

        return file_name

    async def download(self, _, message: types.Message, mystic, fname):
        left_time = {}
        speed_counter = {}

        if os.path.exists(fname):
            return True

        async def downloads():
            async def progress(current, total):
                if current == total:
                    return True

                time_ = time.time()
                start_time = speed_counter.get(message.message_id)
                check_time = time_ + start_time

                if datetime.now() > left_time.get(message.message_id):
                    percentage = current * 100 / total
                    percentage = str(round(percentage, 2))
                    speed = current / check_time

                    total_size = convert_bytes(total)
                    completed_size = convert_bytes(current)
                    speed = convert_bytes(speed)

                    try:
                        await mystic.edit_text("🔍 <b>Downloading...</b>")
                    except:
                        pass

                    left_time[
                        message.message_id
                    ] = datetime.now() + timedelta(seconds=self.sleep)

            try:
                await lolitha.download_media(
                    message.reply_to_message,
                    file_name=fname,
                    progress=progress
                )
                await mystic.edit_text("🔍 <b>Loading...</b>")
                downloader.pop(message.message_id)
            except Exception as e:
                await mystic.edit_text(
                    text=(f"⚠️ <b>Error:</b> {e}\n\n")
                )

        task = asyncio.create_task(downloads())
        xx[mystic.message_id] = task
        await task
        downloaded = downloader.get(message.message_id)
        if downloaded:
            downloader.pop(message.message_id)
            return False

        verify = xx.get(mystic.message_id)
        if not verify:
            return False

        xx.pop(mystic.message_id)
        return True
