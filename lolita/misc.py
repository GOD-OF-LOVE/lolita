from . import log
from .core.mongo_database import mongo_memory


def dbb():
    global db
    db = {}
    log.info("Initialized database...")   
