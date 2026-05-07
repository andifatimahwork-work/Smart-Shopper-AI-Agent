from functools import lru_cache

from pymongo import MongoClient

from .settings import get_settings, require_env


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    settings = get_settings()
    require_env("MONGO_CONNECTION_STRING", settings["mongo_uri"])
    return MongoClient(settings["mongo_uri"])


def get_db():
    settings = get_settings()
    return get_client()[settings["mongo_db"]]


def get_collection(name: str):
    return get_db()[name]
