# utils/logger.py - Utility for logging steps to MongoDB or other sinks

from datetime import datetime
from pymongo import MongoClient
import asyncio
import os
import json
from typing import List, Dict, Any, Set, Optional

# import websockets # Removed as ws_clients will likely store fastapi.WebSocket instances
# For type hinting WebSocket connections if they are FastAPI WebSockets
from fastapi import WebSocket

# --- MongoDB Connection ---
# Consider moving MONGO_URI to .env or config
MONGO_URI = "mongodb://mongo:27017/"
MONGO_DB_NAME = "omnicard"
LOG_COLLECTION_NAME = "logs"
ACCESS_LOG_COLLECTION_NAME = "access_logs"  # New collection for access logs

mongo_client: Optional[MongoClient] = None
log_collection = None
access_log_collection = None  # New collection instance

try:
    print(f"[Logger] Attempting to connect to MongoDB at {MONGO_URI}")
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    mongo_client.admin.command("ping")  # Verify connection
    db = mongo_client[MONGO_DB_NAME]
    log_collection = db[LOG_COLLECTION_NAME]
    access_log_collection = db[ACCESS_LOG_COLLECTION_NAME]  # Initialize new collection
    print(
        f"[Logger] Successfully connected to MongoDB for logging. DB: '{MONGO_DB_NAME}', Collections: '{LOG_COLLECTION_NAME}', '{ACCESS_LOG_COLLECTION_NAME}'"
    )
except Exception as e:
    print(
        f"[Logger] MongoDB connection for logging failed: {e}. Logs will not be saved to DB."
    )
    mongo_client = None
    log_collection = None
    access_log_collection = None

# --- WebSocket Clients Set ---
ws_clients: Set["WebSocket"] = (
    set()
)  # Type hint with forward reference or direct import if safe


async def broadcast_ws(message: str):
    """Broadcasts a message to all connected WebSocket clients."""
    if ws_clients:  # Check if there are any clients connected
        # Use asyncio.gather to run all send tasks concurrently
        # If a client connection is broken, send might raise an exception.
        # It's important to handle such exceptions per client to avoid stopping broadcasts to others.
        tasks = []
        for client in ws_clients:
            tasks.append(client.send_text(message))  # send_text for string messages

        results = await asyncio.gather(*tasks, return_exceptions=True)
        for _, result in enumerate(results):
            if isinstance(result, Exception):
                # Potentially remove the client that caused an error or log the error
                # For simplicity, just printing the error for now
                # A client might have disconnected, which is normal.
                # print(f"[WS Broadcast] Error sending to client {i}: {result}")
                pass  # Silently ignore errors for now to prevent console spam on disconnects


def log_event(event_type: str, data: dict):
    """Logs an event to MongoDB and attempts to broadcast it via WebSocket."""
    now_iso = datetime.utcnow().isoformat()  # Renamed for clarity
    # Log to local file (optional, can be removed if not needed)
    try:
        with open("omnicard_events.log", "a", encoding="utf-8") as f:
            f.write(
                f"[{now_iso}] EventType: {event_type}, Data: {json.dumps(data, default=str)}\n"
            )
    except Exception as file_e:
        print(f"[Logger] Error writing to local event log file: {file_e}")

    entry = {"timestamp": now_iso, "event_type": event_type, "data": data}
    print(f"[LOG_EVENT:{event_type}] @{now_iso} | Data: {data}")

    if log_collection is not None:
        try:
            log_collection.insert_one(entry.copy())
        except Exception as e:
            print(
                f"[Logger] Error saving event log to MongoDB ('{LOG_COLLECTION_NAME}'): {e}"
            )
    else:
        print(
            f"[Logger] MongoDB not available, event log for '{event_type}' not saved to DB."
        )

    # Broadcast via WebSocket
    # This needs to run within an asyncio event loop.
    # FastAPI endpoints running in async mode will have one.
    # If log_event is called from a purely synchronous context without a running loop,
    # this could cause issues. asyncio.get_event_loop().call_soon_threadsafe or similar might be needed
    # for calls from synchronous threads, or ensure log_event is awaited if it becomes async.
    try:
        json_entry = json.dumps(entry, default=str)
        asyncio.create_task(broadcast_ws(json_entry))
    except Exception as e:
        print(
            f"[Logger WS] Error preparing or creating broadcast task for event log: {e}"
        )


# To test WebSocket broadcasting independently (requires a running asyncio loop):
# async def main_test_logger():
#     log_event("test_ws_event", {"message": "Hello WebSocket from logger test"})
#     await asyncio.sleep(1) # Keep loop running for a bit for the task to execute

# if __name__ == "__main__":
#    asyncio.run(main_test_logger())

# Example usage (can be removed or commented out)
# if __name__ == "__main__":
#     log_event("test_event", {"data": "some value", "number": 123})
#     # To test MongoDB, ensure your MongoDB service is running and accessible
#     # and that the "logs" collection exists or can be created by your user.


def log_access_request(
    ip_address: Optional[str],
    user_agent: Optional[str],
    path: str,
    method: str,
    status_code: int,
    extra_data: Optional[dict] = None,
):
    """Logs an access request to the dedicated access_logs MongoDB collection."""
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "path": path,
        "method": method,
        "status_code": status_code,
    }
    if extra_data:
        log_entry["extra_data"] = extra_data

    # print(f"[ACCESS_LOG] IP: {ip_address}, UA: {user_agent}, Path: {path}, Method: {method}, Status: {status_code}")

    if access_log_collection is not None:
        try:
            access_log_collection.insert_one(log_entry.copy())
        except Exception as e:
            print(
                f"[Logger] Error saving access log to MongoDB ('{ACCESS_LOG_COLLECTION_NAME}'): {e}"
            )
    else:
        print(f"[Logger] MongoDB not available, access log for {path} not saved to DB.")

# --- New log_to_mongo and broadcast_log functions ---
MONGO_URI_LOGGER = os.getenv("MONGO_URI_LOGGER", "mongodb://mongo:27017/")
MONGO_DB_NAME_LOGGER = "omnicard_logs"
LOG_COLLECTION_NAME_MONGO = "pipeline_events"

try:
    logger_mongo_client = MongoClient(MONGO_URI_LOGGER, serverSelectionTimeoutMS=3000)
    logger_mongo_client.admin.command("ping")  # Verify connection
    logger_db = logger_mongo_client[MONGO_DB_NAME_LOGGER]
    structured_log_collection = logger_db[LOG_COLLECTION_NAME_MONGO]
    print(
        f"[Logger - MongoDB] Successfully connected for structured logging. DB: '{MONGO_DB_NAME_LOGGER}', Collection: '{LOG_COLLECTION_NAME_MONGO}'"
    )
except Exception as e:
    print(
        f"[Logger - MongoDB] Connection for structured logging failed: {e}."
    )
    structured_log_collection = None

def log_to_mongo(event: str, data: Dict[str, Any]):
    """Logs a structured event to a dedicated MongoDB collection."""
    if structured_log_collection is not None:
        try:
            log_entry = data.copy()
            log_entry["event"] = event
            log_entry["timestamp"] = datetime.utcnow() # Use UTC for consistency
            structured_log_collection.insert_one(log_entry)
            print(f"[Logger - MongoDB] Logged event '{event}' to '{LOG_COLLECTION_NAME_MONGO}'.")
        except Exception as e:
            print(f"[Logger - MongoDB] Error saving event '{event}' to MongoDB: {e}")
    else:
        print(f"[Logger - MongoDB] Not available. Event '{event}' not saved.")

# --- WebSocket Broadcaster ---
# This replaces the old ws_clients set and broadcast_ws logic if this is the new primary way
subscribers: List[WebSocket] = []

async def broadcast_log(message: str):
    """Broadcasts a log message to all subscribed WebSocket clients."""
    # print(f"[WS Broadcast] Attempting to send: {message} to {len(subscribers)} subscribers") # Debug
    # Use a copy of the list for iteration if modification during iteration is possible (though remove handles it)
    for ws in list(subscribers): # Iterate over a copy
        try:
            await ws.send_text(message)
        except Exception as e:
            # print(f"[WS Broadcast] Error sending to a WebSocket client (removing): {e}") # Debug
            # It's crucial to handle disconnections gracefully
            if ws in subscribers: # Check if still there before removing, to handle concurrent removals
                subscribers.remove(ws)
            # Consider logging this error more formally if needed

# --- Old log_event and access_log functions might still be used by other parts or can be deprecated ---
# Keep them for now unless specified to remove

# Old MongoDB connection details (for original log_event)
MONGO_URI_ORIGINAL = "mongodb://mongo:27017/" # Original connection string
MONGO_DB_NAME_ORIGINAL = "omnicard" # Original DB name
LOG_COLLECTION_NAME_ORIGINAL = "logs"
ACCESS_LOG_COLLECTION_NAME_ORIGINAL = "access_logs"

original_mongo_client: Optional[MongoClient] = None
original_log_collection = None
original_access_log_collection = None

try:
    # print(f"[Logger - Original] Attempting to connect to MongoDB at {MONGO_URI_ORIGINAL}")
    original_mongo_client = MongoClient(MONGO_URI_ORIGINAL, serverSelectionTimeoutMS=2000)
    original_mongo_client.admin.command("ping")
    original_db = original_mongo_client[MONGO_DB_NAME_ORIGINAL]
    original_log_collection = original_db[LOG_COLLECTION_NAME_ORIGINAL]
    original_access_log_collection = original_db[ACCESS_LOG_COLLECTION_NAME_ORIGINAL]
    # print(
    #     f"[Logger - Original] Successfully connected to MongoDB for original logging."
    # )
except Exception as e:
    # print(
    #     f"[Logger - Original] MongoDB connection for original logging failed: {e}."
    # )
    original_mongo_client = None
    original_log_collection = None
    original_access_log_collection = None


# Old log_event that writes to omnicard_events.log and original 'logs' collection
def log_event(event_type: str, data: dict):
    """Logs an event to local file and original MongoDB 'logs' collection."""
    now_iso = datetime.utcnow().isoformat()
    try:
        with open("omnicard_events.log", "a", encoding="utf-8") as f:
            f.write(
                f"[{now_iso}] EventType: {event_type}, Data: {json.dumps(data, default=str)}\n"
            )
    except Exception as file_e:
        print(f"[Logger] Error writing to local event log file: {file_e}")

    entry = {"timestamp": now_iso, "event_type": event_type, "data": data}
    # print(f"[LOG_EVENT_ORIGINAL:{event_type}] @{now_iso} | Data: {data}") # Reduce noise if new logger is primary

    if original_log_collection is not None:
        try:
            original_log_collection.insert_one(entry.copy())
        except Exception as e:
            print(f"[Logger - Original] Error saving event log to MongoDB ('{LOG_COLLECTION_NAME_ORIGINAL}'): {e}")
    # else:
        # print(f"[Logger - Original] MongoDB not available, event log for '{event_type}' not saved to DB.")
    
    # Old broadcast logic (commented out if new broadcast_log is primary)
    # try:
    #     json_entry = json.dumps(entry, default=str)
    #     asyncio.create_task(old_broadcast_ws(json_entry)) # Assuming an old_broadcast_ws existed
    # except Exception as e:
    #     print(f"[Logger WS - Original] Error preparing or creating broadcast task for event log: {e}")

def log_access_request(
    ip_address: Optional[str],
    user_agent: Optional[str],
    path: str,
    method: str,
    status_code: int,
    extra_data: Optional[dict] = None,
):
    """Logs an access request to the original access_logs MongoDB collection."""
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "ip_address": ip_address,
        "user_agent": user_agent,
        "path": path,
        "method": method,
        "status_code": status_code,
    }
    if extra_data:
        log_entry["extra_data"] = extra_data

    if original_access_log_collection is not None:
        try:
            original_access_log_collection.insert_one(log_entry.copy())
        except Exception as e:
            print(f"[Logger - Original] Error saving access log to MongoDB ('{ACCESS_LOG_COLLECTION_NAME_ORIGINAL}'): {e}")
    # else:
        # print(f"[Logger - Original] MongoDB not available, access log for {path} not saved to DB.")
