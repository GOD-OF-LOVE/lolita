# encoding utf-8

import httpx
import logging

# Enable the logger
logging.basicConfig(
    level=logging.INFO,
    format="%(name)s.%(funcName)s | %(levelname)s | %(message)s",
    datefmt="[%X]",
)

# To avoid some annoying log
logging.getLogger("pyrogram.syncer").setLevel(logging.WARNING)
logging.getLogger("pyrogram.client").setLevel(logging.WARNING)

log = logging.getLogger(__name__)


# httpx 
timeout = httpx.Timeout(40, pool=None)
http = httpx.AsyncClient(http2=True, timeout=timeout)


from lolithabot.lolitha_class import lolithaTelegramBot
from lolithabot.lolitha_client import lolithaUserbot

self = lolithaTelegramBot()
userbot = lolithaUserbot()


from lolithabot.core.youtube import YouTubeAPI
from lolithabot.core.telegram import TelegramDownload

youtube = YouTubeAPI()
telegram = TelegramDownload()


from lolithabot.misc import dbb
# initilaze database
dbb()
