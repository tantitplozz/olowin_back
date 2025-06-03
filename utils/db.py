# utils/db.py

# import os # Commented out as os.getenv is in the commented MongoDB section
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from typing import Optional

# from workflow.state_schema import AgentState # Commented out as it's not used directly in active code

# --- MongoDB Connection Setup ---
# MONGO_DB_URI = os.getenv("MONGODB_URI", "mongodb://mongo:27017/") # Get from .env or default
# MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "l10_agent_db")
# TASK_COLLECTION_NAME = os.getenv("TASK_COLLECTION_NAME", "tasks")

# For local testing without Docker, you might use "mongodb://localhost:27017/"
MONGO_DB_URI = (
    "mongodb://mongo:27017/"  # Default for Docker Compose service name 'mongo'
)
MONGO_DB_NAME = "omnicard"
TASK_COLLECTION_NAME = "tasks"

client: Optional[MongoClient] = None
db = None
task_collection = None

try:
    print(f"[DB Util] Attempting to connect to MongoDB at {MONGO_DB_URI}")
    client = MongoClient(
        MONGO_DB_URI, serverSelectionTimeoutMS=5000
    )  # 5 second timeout
    client.admin.command("ping")  # Verify connection
    db = client[MONGO_DB_NAME]
    task_collection = db[TASK_COLLECTION_NAME]
    print(
        f"[DB Util] Successfully connected to MongoDB. DB: '{MONGO_DB_NAME}', Collection: '{TASK_COLLECTION_NAME}'"
    )
except ConnectionFailure as e:
    print(f"[DB Util] MongoDB connection failed: {e}. Tasks will not be saved to DB.")
    client = None
    db = None
    task_collection = None
except PyMongoError as e:
    print(
        f"[DB Util] An unexpected error occurred during MongoDB setup: {e}. Tasks will not be saved."
    )
    client = None
    db = None
    task_collection = None


def save_task(task_id: str, state: dict) -> bool:
    """Saves or updates task state in MongoDB. Returns True on success, False on failure."""
    if task_collection is None:
        print(f"[DB Util] MongoDB not available. Cannot save task_id: {task_id}")
        return False
    try:
        result = task_collection.update_one(
            {"task_id": task_id}, {"$set": state}, upsert=True
        )
        print(
            f"[DB Util] Task '{task_id}' saved/updated successfully. Matched: {result.matched_count}, Modified: {result.modified_count}, Upserted ID: {result.upserted_id}"
        )
        return True
    except PyMongoError as e:
        print(f"[DB Util] Error saving task '{task_id}' to MongoDB: {e}")
        return False


def get_task(task_id: str):
    """Retrieves task state from MongoDB by task_id."""
    if task_collection is None:
        print(f"[DB Util] MongoDB not available. Cannot get task_id: {task_id}")
        return None
    try:
        task_data = task_collection.find_one({"task_id": task_id})
        if task_data:
            task_data.pop("_id", None)
            print(f"[DB Util] Task '{task_id}' retrieved successfully.")
            return task_data
        print(f"[DB Util] Task '{task_id}' not found in DB.")
        return None
    except PyMongoError as e:
        print(f"[DB Util] Error retrieving task '{task_id}' from MongoDB: {e}")
        return None


# Example of converting AgentState (TypedDict) to a plain dict for MongoDB
# This is already implicitly handled if AgentState is used as a dict,
# but explicit conversion can be more robust if AgentState becomes a class.
# def agent_state_to_dict(state: AgentState) -> Dict[str, Any]:
#     return dict(state)

# def dict_to_agent_state(data: Dict[str, Any]) -> AgentState:
#     # This would require careful handling if AgentState has complex types or defaults
#     # For now, assuming direct cast works if structure matches.
#     return AgentState(**data) # This might fail if AgentState has non-optional fields not in data

# To ensure schema compatibility, when saving initial_state in ui_server.py,
# it's good practice to convert the AgentState TypedDict to a plain dict.
# initial_state.dict() is not a method of TypedDict. It should just be `dict(initial_state)` or `initial_state` directly if it's already dict-like.
# For retrieving, ensure the dict from MongoDB can be cast back or used to reconstruct AgentState.
