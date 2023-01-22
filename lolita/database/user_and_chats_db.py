from lolithabot.core.mongo_database import mongo_database


chat_database = mongo_database.chats

async def get_served_chats() -> list:
    chats_list = []
    async for chat in chat_database.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat)
    return chats_list


async def is_served_chat(chat_id: int) -> bool:
    chat = await chat_database.find_one({"chat_id": chat_id})
    if not chat:
        return False
    return True


async def add_served_chat(chat_id: int):
    is_served = await is_served_chat(chat_id)
    if is_served:
        return
    return await chat_database.insert_one({"chat_id": chat_id})


user_database = mongo_database.usersdb

async def is_served_user(user_id: int) -> bool:
    user = await user_database.find_one({"user_id": user_id})
    if not user:
        return False

    return True


async def get_served_users() -> list:
    users_list = []
    async for user in user_database.find({"user_id": {"$gt": 0}}):
        users_list.append(user)
    return users_list


async def add_served_user(user_id: int):
    is_served = await is_served_user(user_id)
    if is_served:
        return
    return await user_database.insert_one({"user_id": user_id})


blaclist_database = mongo_database.blacklistchat

async def blacklisted_chats() -> list:
    chats_list = []
    async for chat in blacklist_database.find({"chat_id": {"$lt": 0}}):
        chats_list.append(chat["chat_id"])
    return chats_list


async def blacklist_chat(chat_id: int) -> bool:
    if not await blacklist_database.find_one({"chat_id": chat_id}):
        await blacklist_database.insert_one({"chat_id": chat_id})
        return True
    return False


async def whitelist_chat(chat_id: int) -> bool:
    if await blacklist_database.find_one({"chat_id": chat_id}):
        await blacklist_database.delete_one({"chat_id": chat_id})
        return True
    return False
