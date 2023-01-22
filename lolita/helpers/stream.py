# encoding utf-8

import os
import config

from random import randint
from typing import Union
from pyrogram import enums

from lolithabot import self, log, youtube
from lolithabot.misc import db
from lolithabot.database import (
    add_active_chat,
    add_active_video_chat,
    is_active_chat,
    is_video_allowed, 
    music_on
)
from lolithabot.helpers.queue import put_queue, put_queue_index 
from lolithabot.core.group_call import call


async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    forceplay: Union[bool, str] = None
):
    if not result:
        return

    if video:
        if not await is_video_allowed(chat_id):
            return

    if forceplay:
        await call.force_stop_stream(chat_id)

    if streamtype == "youtube":
        link = result["link"]
        title = (result["title]).title()
        vidid = result["vidid"]
        duration_min = result["duration_min"]
        status = True if video else None

        try:
            file_path, direct = await youtube.download(
                vidid, 
                mystic,
                videoid=True, 
                video=status
            )
        except Exception as e:
            return await mystic.edit_text("<b>Error:</b> " + str(e))

        active = await is_active_chat(chat_id)
        if active:
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            await mystic.edit_text(
                text=(
                    f"➕ Added to queue\n"
                    f"📌 Position N°{position}\n\n"
                    f"🎼 <b>Name:</b> <a href='{link}'>{title}</a>\n"
                    f"⏱ <b>Duration:</b> <pre>{duration_min}</pre>\n"
                    f"✨ <b>Requested by:</b> <a href='tg://user?id={user_id}'>{user_name}</a>"
                ),
                disable_web_page_preview=True,
                parse_mode=enums.parse_mode.ParseMode.HTML
            )

        else:
            if not forceplay:
                db[chat_id] = []

            await call.join_call(
                chat_id, original_chat_id, file_path, video=status
            )
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )
            run = await mystic.edit_text(
                text=(
                    f"➕ <b>New streaming</b>\n"
                    f"🎼 <b>Name:</b> <a href='{link}'>{title}</a>\n"
                    f"⏱ <b>Duration:</b> <pre>{duration_min}</pre>\n"
                    f"📌 <b>Requested by:</b> <a href='tg://user?id={user_id}'>{user_name}</a>"
                ),
                disable_web_page_preview=True,
                parse_mode=enums.parse_mode.ParseMode.HTML
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"

    elif streamtype == "telegram":
        link = result["link"]
        title = (result["title"]).title()
        file_path = result["path"]
        duration_min = result["dur"]
        status = True if video else None

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            await mystic.edit_text(
                text=(
                    f"➕ Added to queue\n"
                    f"📌 Position N°{position}\n\n"
                    f"🎼 <b>Name:</b> <a href='{link}'>{title}</a>\n"
                    f"⏱ <b>Duration:</b> <pre>{duration_min}</pre>\n"
                    f"✨ <b>Requested by:</b> <a href='tg://user?id={user_id}'>{user_name}</a>"
                ),
                disable_web_page_preview=True,
                parse_mode=enums.parse_mode.ParseMode.HTML
            )

        else:
            if not forceplay:
                db[chat_id] = []

            await call.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=status
            )
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

            run = await mystic.edit_text(
                text=(
                    f"➕ <b>New streaming</b>\n"
                    f"🎼 <b>Name:</b> <a href='{link}'>{title}</a>\n"
                    f"⏱ <b>Duration:</b> <pre>{duration_min}</pre>\n"
                    f"📌 <b>Requested by:</b> <a href='tg://user?id={user_id}'>{user_name}</a>"
                ),
                disable_web_page_preview=True,
                parse_mode=enums.parse_mode.ParseMode.HTML
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

    elif streamtype == "live":
        link = result["link"]
        title = (result["title"]).title()
        vidid = result["vidid"]
        status = True if video else None
        duration_min = "Live streaming."
        active = await is_active_chat(chat_id)
        if active:
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            await mystic.edit_text(
                text=(
                    f"➕ Added to queue\n"
                    f"📌 Position N°{position}\n\n"
                    f"🎼 <b>Name:</b> <a href='{link}'>{title}</a>\n"
                    f"⏱ <b>Duration:</b> {duration_min}\n"
                    f"✨ <b>Requested by:</b> <a href='tg://user?id={user_id}'>{user_name}</a>"
                ),
                disable_web_page_preview=True,
                parse_mode=enums.parse_mode.ParseMode.HTML
            )

        else:
            if not forceplay:
                db[chat_id] = []

            mia_khalifa, file_path = await youtube.video(link)
            if mia_khalifa == 0:
                return await mystic.edit_text("Unable to stream YouTube live streaming.")

            await call.join_call(
                chat_id, original_chat_id, file_path, video=status
            ) 
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if video else "audio",
                forceplay=forceplay,
            )

            run = await mystic.edit_text(
                text=(
                    f"➕ <b>New streaming</b>\n"
                    f"🎼 <b>Name:</b> <a href='{link}'>{title}</a>\n"
                    f"⏱ <b>Duration:</b> {duration_min}\n"
                    f"📌 <b>Requested by:</b> <a href='tg://user?id={user_id}'>{user_name}</a>"
                ),
                disable_web_page_preview=True,
                parse_mode=enums.parse_mode.ParseMode.HTML
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
