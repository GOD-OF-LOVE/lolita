import sys
import asyncio
import importlib

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config

from lolithabot import self, log, userbot
from lolithabot.plugins import all_modules
from lolithabot.core.group_call import call
            

async def init(): 
    if (
        not config.SessionString
        and not config.SessionString2
    ):
        log.error(
            "Exiting the program, Session assistant not defined."
        )
        return
 
    # loaded the all modules
    for all_module in all_modules:
        print("Loaded the all modules")
        importlib.import_module("lolithabot.plugins" + all_module)
 
    await self.start()   
    await userbot.start()
    await call.start()

    try:
        await call.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        log.error(
            "[Error]: No active group call, make sure you never ended the video chat."
        )
        sys.exit()

    except:
        pass

    await call.decorators()
    log.info("lolitha: the bot started successfully.")
    await idle()


if __name__ == "__main__":
    # asyncio event loop
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
