import random

from lolithabot import userbot
from lolithabot.core.mongo_database import mongo_database

database = mongo_database.assistants

assistantdict = {}


async def get_client(assistant: int):
    if int(assistant) == 1:
        return userbot.one

    elif int(assistant) == 2:
        return userbot.second


async def set_assistant(chat_id):
    from lolithabot.lolitha_client import clients

    ran_assistant = random.choice(clients)
    assistantdict[chat_id] = ran_assistant
    await database.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    userbot = await get_client(ran_assistant)
    return userbot


async def get_assistant(chat_id: int) -> str:
    from lolithabot.lolitha_client import clients

    assistant = assistantdict.get(chat_id)
    if not assistant:
        dbassistant = await database.find_one({"chat_id": chat_id})
        if not dbassistant:
            userbot = await set_assistant(chat_id)
            return userbot
        else:
            got_assis = dbassistant["assistant"]
            if got_assis in clients:
                assistantdict[chat_id] = got_assis
                userbot = await get_client(got_assis)
                return userbot
            else:
                userbot = await set_assistant(chat_id)
                return userbot
    else:
        if assistant in clients:
            userbot = await get_client(assistant)
            return userbot
        else:
            userbot = await set_assistant(chat_id)
            return userbot


async def set_calls_assistant(chat_id):
    from lolithabot.lolitha_client import clients

    ran_assistant = random.choice(clients)
    assistantdict[chat_id] = ran_assistant
    await database.update_one(
        {"chat_id": chat_id},
        {"$set": {"assistant": ran_assistant}},
        upsert=True,
    )
    return ran_assistant


async def group_assistant(self, chat_id: int) -> int:
    from lolithabot.lolitha_client import clients

    assistant = assistantdict.get(chat_id)
    if not assistant:
        dbassistant = await database.find_one({"chat_id": chat_id})
        if not dbassistant:
            assis = await set_calls_assistant(chat_id)
        else:
            assis = dbassistant["assistant"]
            if assis in clients:
                assistantdict[chat_id] = assis
                assis = assis
            else:
                assis = await set_calls_assistant(chat_id)
    else:
        if assistant in clients:
            assis = assistant
        else:
            assis = await set_calls_assistant(chat_id)

    if int(assis) == 1:
        return self.one

    elif int(assis) == 2:
        return self.second
