# loggers/dataset_logger.py
import json
import os
from datetime import datetime

LOG_DIR = "datasets"

def log_dataset(agent_name: str, data: dict):
    """
    บันทึกข้อมูล (รวม prompt/response/feedback) ลงไฟล์ .jsonl 
    โดยใช้ agent_name (หรือ model_name) เป็นส่วนหนึ่งของชื่อไฟล์.
    เพิ่ม timestamp ให้กับ data ก่อนบันทึก.
    """
    try:
        os.makedirs(LOG_DIR, exist_ok=True)

        # Sanitize agent_name for filename
        safe_agent_name = str(agent_name).replace("/", "_").replace("\\", "_")
        filename = os.path.join(LOG_DIR, f"{safe_agent_name}_log.jsonl")
        
        # Add timestamp to the data dictionary itself
        data_to_log = data.copy() # Avoid modifying original dict if passed around
        data_to_log["timestamp"] = datetime.utcnow().isoformat() # Use UTC for consistency

        with open(filename, "a", encoding="utf-8") as f:
            f.write(json.dumps(data_to_log, ensure_ascii=False) + "\n")
        print(f"[DatasetLogger] Logged data for '{agent_name}' to {filename}. Keys: {list(data_to_log.keys())}")
    except Exception as e:
        print(f"[DatasetLogger] Error logging dataset for '{agent_name}': {e}") 