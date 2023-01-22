# encoding utf-8

import asyncio

from typing import Union
from datetime import datetime, timedelta

from pyrogram import Client, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    ChatAdminRequired,
    UserNotParticipant,
    UserAlreadyParticipant
)

from pytgcalls import PyTgCalls, StreamType
from pytgcalls.types import (
    JoinedGroupCallParticipant,
    LeftGroupCallParticipant, 
    Update
)
from pytgcalls.exceptions import (
    AlreadyJoinedError,
    NoActiveGroupCall,
    TelegramServerError 
)
from pytgcalls.types.stream import StreamAudioEnded
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped

import config
from lolithabot import self as lolitha, log, youtube
from lolithabot.misc import db
from lolithabot.database import (
    add_active_chat,
    add_active_video_chat,
    get_assistant,
    get_audio_bitrate, 
    get_loop, 
    get_video_bitrate,
    group_assistant, 
    is_autoend,
    music_on, 
    mute_off,
    remove_active_chat,
    remove_active_video_chat,
    set_loop
)
from lolithabot.helpers.auto_clears import auto_clean


counter = {}
auto_ended = {}
auto_end_time = 3


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class AssistantErr(Exception):
    def __init__(self, errr: str):
        super().__init__(errr)


class GroupCall(PyTgCalls):
    def __init__(self):
        ubot = self.__class__.__name__.lower()
        self.userbot1 = Client(
            name=ubot,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.SessionString)
        )
        self.one = PyTgCalls(self.userbot1, cache_duration=100)
        
        # userbot 2
        self.userbot2 = Client(
            name=ubot,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.SessionString2)
        )
        self.second = PyTgCalls(self.userbot2, cache_duration=100)

    async def pause_stream(self, chat_id: int):
        assinstant = await group_assistant(self, chat_id)
        await assistant.pause_stream(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_stream(chat_id)

    async def mute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.mute_stream(chat_id)

    async def unmute_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.unmute_stream(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_group_call(chat_id)
        except:
            pass

    async def force_stop_playing(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except:
            pass

        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_group_call(chat_id)
        except:
            pass  

    async def skip_stream(
        self, chat_id: int, link: str, video: Union[bool, str] = None
    ):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        stream = (
            AudioVideoPiped(
                link,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality
            )
            if video
            else AudioPiped(
                link, audio_parameters=audio_stream_quality
            )
        )
        await assistant.change_stream(chat_id, stream)

    async def seek_stream(
        self, chat_id, file_path, to_seek, duration, mode
    ):
        assistant = await group_assitant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        stream = (
            AudioVideoPiped(
                file_path,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality,
                additional_ffmpeg_parameters=f'-ss {to_seek} -to {duration}'
            )
            if mode == "video"
            else AudioPiped(
                file_path,
                audio_parameters=audio_stream_quality,
                additional_ffmpeg_parameters=f'-ss {to_seek} -to {duration}'  
            )
        ) 
        await assistant.change_stream(chat_id, stream) 

    async def stream_call(self, link):
        assistant = await group_assistant(self, chat_id)
        await assistant.join_group_call(
            config.log_chat,
            AudioVideoPiped(link),
            stream_type=StreamType().pulse_stream
        )
        await asyncio.sleep(5)
        await assistant.leave_group_call(config.log_chat)

    async def join_assistant(self, original_chat_id, chat_id):
        userbot = await get_assistant(chat_id)
        try:
            try:
                users = await lolitha.get_chat_member(chat_id, userbot.id)
            except ChatAdminRequired:
                raise AssistantErr("The bot doesn't have permission to invite userbot to group.")

            if users.status == enums.ChatMemberStatus.BANNED:
                text_message = (
                    "😕 The userbot @{} [<pre>{}</pre>] has been <b>banned</b> on this group.\n\n"
                    "⚠️ <i>If you think this is an error please report it in the "
                    "<a href='https://t.me/lolithaBotSupport'>support group</a></i>."
                )
                await lolitha.send_message(
                    chat_id=chat_id,
                    text=text_message.format(userbot.username, userbot.id),
                    disable_web_page_preview=True,
                    parse_mode=enums.parse_mode.ParseMode.HTML
                )
        except UserNotParticipant:
            chat = await lolitha.get_chat(chat_id)
            if chat.username:
                try:
                    await userbot.join_chat(chat.username)
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    await lolitha.send_message(
                        chat_id=chat_id,
                        text=(
                            f"⚠️ <b>Error:</b> <pre>{str(e)}</pre>"
                        ),
                        parse_mode=enums.parse_mode.ParseMode.HTML
                    )
            else:
                try:
                    try:
                        try:
                            invite_link = chat.invite_link
                            if invite_link is None:
                                invite_link = (await lolitha.export_chat_invite_link(chat_id))
                        except:
                            invite_link = (await lolitha.export_chat_invite_link(chat_id))

                    except ChatAdminRequired:
                        raise AssistantErr(
                            "👮🏻‍♂️ <b>Set me up as admin so I can work</b> (<b>Missing Permissions:</b> <pre>Add Members</pre>\n\n"
                            "⚠️ <i>If you think this is an error please report it in the "
                            "<a href='https://t.me/lolithaBotSupport'>support group</a></i>."
                        )
                    except Exception as e:
                        raise AssistantErr(e)

                    message_wait = await lolitha.send_message(
                        chat_id=chat_id, 
                        text=(
                            f"@{userbot.username} [<pre>{userbot.id}</pre>] "
                            + "<i>the userbot will be joining in 5 seconds</i>."
                        ),
                        parse_mode=enums.parse_mode.ParseMode.HTML
                    )
                    await asyncio.sleep(3)
                    await userbot.join_chat(invite_link)
                    await asyncio.sleep(4)
                    await message_wait.edit(f"✅ @{userbot.username} successfully joined this group.")
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    raise AssistantErr(
                        f"Exception occured while inviting <b>Userbot account</b> "
                        f"to this group.\n<b>Due to:</b> {str(e)}"
                    )

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None
    ):
        assistant = await group_assistant(self, chat_id)
        audio_stream_quality = await get_audio_bitrate(chat_id)
        video_stream_quality = await get_video_bitrate(chat_id)
        stream = (
            AudioVideoPiped(
                link,
                audio_parameters=audio_stream_quality,
                video_parameters=video_stream_quality
            )
            if video
            else AudioPiped(
                link, audio_parameters=audio_stream_quality
            )
        )
        try:
            await assistant.join_group_call(
                chat_id,
                stream,
                stream_type=StreamTyoe().pulse_stream
            )
        except NoActiveGroupCall:
            try:
                await self.join_assistant(original_chat_id, chat_id)
            except Exception as e:
                raise e

            try:
                await assistant.join_group_call(
                    chat_id,
                    stream,
                    stream_type=StreamType().pulse_stream
                )
            except Exception as e:
                raise AssistentErr("🚫 <pre>{e}</pre>".format(e)) 

        except AlreadyJoinedError:
            raise AssistentErr("Userbot already joined into the group call.")

        except TelegramServerError:
            raise AssistentErr(
                "🚫 <b>Telegram server error</b>\n\n"
                "• Telegram is having some internal server problems. Please try playing again.\n"
                "If this problem keeps coming everytime, please end your video chat and start fresh video chat again."
            )

        await add_active_chat(chat_id)
        await mute_off(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)

        auto_stop = await is_autoend()
        if auto_stop:
            counter[chat_id] = {}
            user_in_video_chats = len(await assistant.get_participants(chat_id))
            if user_in_video_chats == 1:
                auto_ended[chat_id] = datetime.now() + timedelta(
                    minutes=auto_end_time
                )  

    async def change_stream(self, client, chat_id):        
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)

            if popped:
                if config.AUTO_DOWNLOADS_CLEAR:
                    await auto_clean(popped)

            if not check:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)

        except:
            try:
                await _clear_(chat_id)
                return await client.leave_group_call(chat_id)
            except:
                return

        else:
            user = check[0]["by"]
            queue = check[0]["file"] 
            title = (check[0]["title"]).title()  
            videoid = check[0]["vidid"]
            duration = check[0]["dur"]
            streamtype = check[0]["streamtype"]
            original_chat_id = check[0]["chat_id"]
            check[0]["played"] = 0
            audio_stream_quality = await get_audio_bitrate(chat_id)
            video_stream_quality = await get_video_bitrate(chat_id)
            if "live_" in queue:
                x, link = await youtube.video(videoid, True)
                if x == 0:
                    return await lolitha.send_message(
                        original_chat_id,
                        text="😕 Sorry, failed to skip the song, please try again with the same command."
                    )

                stream = (
                    AudioVideoPiped(
                        link,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality
                    )
                    if str(streamtype) == "video"
                    else AudioPiped(
                        link, audio_parameters=audio_stream_quality
                    )
                )
                try:
                    await client.change_stream(chat_id, stream)
                except Exception as e:
                    await lolitha.send_message(
                        original_chat_id,
                        text=f"🚫 <b>Error:</b> <pre>{e}</pre>"
                    )
                    return

                run = await lolitha.send_message(
                    original_chat_id,
                    text=(
                        f"➕ <b>New streaming</b>\n"
                        f"🎼 <b>Name:</b> <a href='https://www.youtube.com/watch?v={videoid}'>{title}</a>\n"
                        f"⏱ <b>Duration:</b> <pre>{duration}</pre>\n"
                        f"📌 <b>Requested by:</b> {user}"
                    ),
                    disable_web_page_preview=True,
                    parse_mode=enums.parse_mode.ParseMode.HTML
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

            elif "vid_" in queue:
                try:
                    file_path, direct = await youtube.download(
                        videoid,
                        videoid=True,
                        video=True
                        if str(streamtype) == "video"
                        else False,
                    )
                except Exception as e:
                    await lolitha.send_message(
                        original_chat_id,
                        text=(f"<b>Error encurred:</b> <pre>{e}</pre>"),
                        parse_mode=enums.parse_mode.ParseMode.HTML
                    ) 
                    return 

                stream = (
                    AudioVideoPiped(
                        file_path,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality,
                    )
                    if str(streamtype) == "video"
                    else AudioPiped(
                        file_path,
                        audio_parameters=audio_stream_quality,
                    )
                )
                try:
                    await client.change_stream(chat_id, stream)
                except Exception as e:
                    await lolitha.send_message(
                        original_chat_id,
                        text=(f"<b>Error encurred:</b> <pre>{e}</pre>"),
                        parse_mode=enums.parse_mode.ParseMode.HTML
                    )
                    return 

                run = await lolitha.send_message(
                    original_chat_id,
                    text=(
                        f"➕ <b>New streaming</b>\n"
                        f"🎼 <b>Name:</b> <a href='https://www.youtube.com/watch?v={videoid}'>{title}</a>\n"
                        f"⏱ <b>Duration:</b> <pre>{duration}</pre>\n"
                        f"📌 <b>Requested by:</b> {user}"
                    ),
                    disable_web_page_preview=True,
                    parse_mode=enums.parse_mode.ParseMode.HTML
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"

            elif "index_" in queue:
                stream = (
                    AudioVideoPiped(
                        videoid,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality,
                    )
                    if str(streamtype) == "video"
                    else AudioPiped(
                        videoid, audio_parameters=audio_stream_quality
                    )
                )
                try:
                    await client.change_stream(chat_id, stream)
                except Exception as e:
                    await lolitha.send_message(
                        original_chat_id,
                        text=(f"<b>Error encurred:</b> <pre>{e}</pre>"),
                        parse_mode=enums.parse_mode.ParseMode.HTML
                    )
                    return

                run = await lolitha.send_message(
                    original_chat_id,
                    text=(
                        f"➕ <b>New streaming</b>\n"
                        f"🎼 <b>Name:</b> <a href='https://www.youtube.com/watch?v={videoid}'>{title}</a>\n"
                        f"⏱ <b>Duration:</b> <pre>{duration}</pre>\n"
                        f"📌 <b>Requested by:</b> {user}"
                    ),
                    disable_web_page_preview=True,
                    parse_mode=enums.parse_mode.ParseMode.HTML
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"

            else:
                stream = (
                    AudioVideoPiped(
                        queued,
                        audio_parameters=audio_stream_quality,
                        video_parameters=video_stream_quality,
                    )
                    if str(streamtype) == "video"
                    else AudioPiped(
                        queued, audio_parameters=audio_stream_quality
                    )
                )
                try:
                    await client.change_stream(chat_id, stream)
                except Exception as e:
                    await lolitha.send_message(
                        original_chat_id,
                        text=(f"<b>Error encurred:</b> <pre>{e}</pre>"),
                        parse_mode=enums.parse_mode.ParseMode.HTML
                    )
                    return

                if videoid == "telegram":
                    run = await lolitha.send_message(
                        original_chat_id,
                        text=(
                            f"➕ <b>New streaming</b>\n"
                            f"🎼 <b>Name:</b> {title}\n"
                            f"⏱ <b>Duration:</b> <pre>{duration}</pre>\n"
                            f"📌 <b>Requested by:</b> {user}"
                        ),
                        disable_web_page_preview=True,
                        parse_mode=enums.parse_mode.ParseMode.HTML
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"

                else:
                    run = await lolitha.send_message(
                        original_chat_id,
                        text=(
                            f"➕ <b>New streaming</b>\n"
                            f"🎼 <b>Name:</b> <a href='https://www.youtube.com/watch?v={videoid}'>{title}</a>\n"
                            f"⏱ <b>Duration:</b> <pre>{duration}</pre>\n"
                            f"📌 <b>Requested by:</b> {user}"
                        ),
                        disable_web_page_preview=True,
                        parse_mode=enums.parse_mode.ParseMode.HTML
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"  

    async def ping(self):
        pings = []
        if config.SessionString:
            pings.append(await self.one.ping)

        if config.SessionString2:
            pings.append(await self.second.ping) 

        return str(round(sum(pings) / len(pings), 3))

    async def start(self):
        log.info("Starting PyTgCalls Client\n")
        if config.SessionString:
            await self.one.start()

        if config.SessionString2:
            await self.second.start()

    async def decorators(self):
        @self.one.on_kicked()
        @self.second.on_kicked()        
        @self.one.on_closed_voice_chat()
        @self.second.on_closed_voice_chat()       
        @self.one.on_left()
        @self.second.on_left()
        async def stream_services_handler(_, chat_id: int):
            await self.stop_stream(chat_id)

        @self.one.on_stream_end()
        @self.second.on_stream_end()
        async def stream_end_handler1(client, update: Update):
            if not isinstance(update, StreamAudioEnded):
                return

            await self.change_stream(client, update.chat_id)

        @self.one.on_participants_change()
        @self.second.on_participants_change()
        async def participants_change_handler(client, update: Update):
            if not isinstance(
                update, JoinedGroupCallParticipant
            ) and not isinstance(update, LeftGroupCallParticipant):
                return

            chat_id = update.chat_id
            users = counter.get(chat_id)

            if not users:
                try:
                    got = len(await client.get_participants(chat_id))
                except:
                    return
                counter[chat_id] = got
                if got == 1:
                    auto_ended[chat_id] = datetime.now() + timedelta(
                        minutes=auto_end_time
                    )
                    return
                auto_ended[chat_id] = {}

            else:
                final = (
                    users + 1
                    if isinstance(update, JoinedGroupCallParticipant)
                    else users - 1
                )
                counter[chat_id] = final
                if final == 1:
                    auto_ended[chat_id] = datetime.now() + timedelta(
                        minutes=auto_end_time
                    )
                    return

                auto_ended[chat_id] = {}


call = GroupCall()                                                            
