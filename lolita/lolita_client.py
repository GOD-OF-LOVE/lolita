import sys
import config
import pyrogram

from lolithabot import log

clients = []
assistant = []

class lolithaUserbot(pyrogram.Client):
    def __init__(self):
        ubot = self.__class__.__name__.lower()
        self.one = pyrogram.Client(
            name=ubot,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.SessionString,
            no_updates=True
        )
        self.second = pyrogram.Client(
            name=ubot,
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=config.SessionString2,
            no_updates=True
        )

    async def start(self):
        log.info('Starting lolitha userbot...')
        if config.SessionString:
            await self.one.start()
            clients.append(1)
            try:
                await self.one.send_message(
                    chat_id=config.log_chat,
                    text=("✅ Assistant has been started.")
                )
            except:
                log.error(
                    "Assistant account has failed to acces the log group."
                )
                sys.exit()
     
            client_id = (await self.one.get_me()).id
            assistant.append(client_id)
            log.info("lolitha userbot 1 has been started.")

        if config.SessionString2:
            await self.second.start()
            clients.append(2)
            try:
                await self.second.send_message(
                    chat_id=config.log_chat,
                    text="✅ Assistant has been started." 
                )
            except:
                log.error(
                    "Assistant 2 account has failed to acces the log group."
                )
                sys.exit()

            client_id = (await self.second.get_me()).id
            assistant.append(client_id)
            log.info("lolitha userbot 2 has been started.")                  
