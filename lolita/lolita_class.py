import time, psutil, logging, datetime

from pyrogram.errors import BadRequest
from pyrogram.enums.parse_mode import ParseMode
from pyrogram import Client, __version__ as vers

from pytgcalls.__version__ import __version__

import config


log = logging.getLogger(__name__)

class lolithaTelegramBot(Client):
    def __init__(self):
        lolitha = self.__class__.__name__.lower()

        super().__init__(
            name=lolitha,
            api_id=config.API_ID,
            api_hash=config.API_HASH,  
            bot_token=config.TELEGRAM,
            in_memory=True
        ) 

    async def start(self):
        await super().start()

        self.me = await self.get_me()
        self.username = self.me.username
        self.first_name = self.me.first_name
        self.start_time = time.time()

        log.info(
            "lolitha music running with Pyrogram v%s (Layer %s) started on @%s. Hi!",
            vers,
            self.me.username,
        )
        bot_time = datetime.datetime.fromtimestamp(psutil.boot_time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        start_message = (
            f'<b>{self.first_name} Actived</b>\n'
            f'    <b>version:</b> <code>v0.0.0</code>\n'
            f'    <b>pyrogram:</b> <code>v{vers}</code>\n'
            f'    <b>py-tgcalls:</b> <code>v{__version__}</code>\n'
            f'    <b>start_time:</b> <code>{bot_time}</code>'
        )
        await self.send_message(
            chat_id=config.log_chat, text=start_message, parse_mode=ParseMode.HTML
        )

    async def stop(self):
        await super().stop()
        log.warning("lolitha Stopped")
