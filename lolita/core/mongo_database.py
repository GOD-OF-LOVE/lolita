from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient

import config
from lolithabot import self, log


MongoDB = (
    'mongodb+srv://rizexx:bdg12345..@cluster0.qzxaj.mongodb.net/myFirstDatabase?retryWrites=true&w=majority'
)
if config.MongoDatabaseURI is None:
    log.warning(
        'Database not found, please add the mongo uri database.'
    )
    self_get = self.get_me()
    self_username = self_get.username

    mongo_async = AsyncIOMotorClient(MongoDB)
    mongo_syncs = MongoClient(MongoDB)
    mongo_database = mongo_async[self_username]
    mongo_memory = mongo_syncs[self_username]
else:
    mongo_async = AsyncIOMotorClient(config.MongoDatabaseURI)
    mongo_syncs = MongoClient(config.MongoDatabaseURI)
    mongo_database = mongo_async.self_username
    mongo_memory = mongo_syncs.self_username
