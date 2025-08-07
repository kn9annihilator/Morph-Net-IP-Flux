# core/status_manager.py

import json
import os
import logging
from datetime import datetime, timezone

STATUS_FILE = "logs/status.json"

def update_status(status_data: dict):
    """
    Writes the current status of the MTD engine to a JSON file.

    Args:
        status_data (dict): A dictionary containing the current state.
    """
    try:
        # Add a timestamp to know how fresh the data is
        status_data['last_updated_utc'] = datetime.now(timezone.utc).isoformat()
        
        os.makedirs("logs", exist_ok=True)
        with open(STATUS_FILE, 'w') as f:
            json.dump(status_data, f, indent=2)
    except IOError as e:
        logging.error(f"Failed to write to status file {STATUS_FILE}: {e}")

def read_status() -> dict:
    """
    Reads the current status from the JSON file.

    Returns:
        dict: The last known status, or a default dictionary if not found.
    """
    if not os.path.exists(STATUS_FILE):
        return {"status": "Initializing..."}
    
    try:
        with open(STATUS_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {"status": "Error reading status file."}