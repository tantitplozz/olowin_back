from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Dict, Any

mongo: MongoClient = MongoClient("mongodb://mongo:27017")
memory_db: Collection[Dict[str, Any]] = mongo["omnicard"]["memory"]


def store_memory(task_id: str, key: str, value: Dict[str, Any]):
    memory_db.update_one({"task_id": task_id}, {"$set": {key: value}}, upsert=True)


def load_memory(task_id: str) -> Dict[str, Any] | None:
    return memory_db.find_one({"task_id": task_id})
