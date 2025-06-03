# loggers/dataset_logger.py
from pymongo import MongoClient
import os
from datetime import datetime
import json

# Fallback JSONL logging if MongoDB is not available
JSONL_LOG_DIR = "datasets"

class DatasetLogger:
    def __init__(self):
        uri = os.getenv("MONGODB_URI")
        self.client = None
        self.db = None
        if uri:
            try:
                self.client = MongoClient(uri, serverSelectionTimeoutMS=5000)
                # Verify connection
                self.client.admin.command('ping') 
                self.db = self.client.omnicard # Database name
                print("[DatasetLogger] Successfully connected to MongoDB.")
            except Exception as e:
                print(f"[DatasetLogger] Failed to connect to MongoDB: {e}. Falling back to JSONL logging.")
                self.client = None # Ensure client is None if connection failed
        else:
            print("[DatasetLogger] MONGODB_URI not found. Falling back to JSONL logging.")

    def log(self, prompt: str, response: str, agent_name: str = "unknown_agent"):
        timestamp = datetime.utcnow()
        log_entry = {
            "prompt": prompt,
            "response": response,
            "agent_name": agent_name,
            "timestamp": timestamp.isoformat()
        }
        
        if self.db:
            try:
                self.db.logs.insert_one(log_entry) # Collection name 'logs'
            except Exception as e:
                print(f"[DatasetLogger] Error logging to MongoDB: {e}. Attempting JSONL fallback.")
                self._log_to_jsonl(log_entry, agent_name) # Fallback to JSONL if DB write fails
        else:
            self._log_to_jsonl(log_entry, agent_name)

    def _log_to_jsonl(self, data_to_log: dict, agent_name: str):
        """Fallback to log data to a .jsonl file."""
        try:
            os.makedirs(JSONL_LOG_DIR, exist_ok=True)
            safe_agent_name = str(agent_name).replace("/", "_").replace("\\", "_")
            filename = os.path.join(JSONL_LOG_DIR, f"{safe_agent_name}_fallback_log.jsonl")
            
            with open(filename, "a", encoding="utf-8") as f:
                f.write(json.dumps(data_to_log, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[DatasetLogger] Error in JSONL fallback logging for '{agent_name}': {e}")

# Global instance
logger = DatasetLogger() 