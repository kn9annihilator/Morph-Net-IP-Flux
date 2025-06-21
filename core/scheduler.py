"""
Module: core/scheduler.py

Purpose:
Controls timed rotation of IP addresses using jittered/random scheduling.
Loads IP pool from config, selects new IPs, and invokes the IP rotation logic.
Can be extended to integrate with DNS, logging services, and decoy infrastructure.
"""

import time
import random
import yaml
import logging
import os
from datetime import datetime
from core.ip_manager import rotate_ip

# Define project base and config paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "default_config.yaml")
LOG_FILE = os.path.join(BASE_DIR, "logs", "rotation.log")

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_ip_pool(config_path: str = CONFIG_PATH) -> dict:
    """
    Loads IP rotation pool and settings from YAML configuration file.

    Returns:
        dict: Configuration data including IP pool and timing settings.
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            return config
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return {}

def jittered_interval(min_sec: int, max_sec: int) -> int:
    """
    Returns a random interval between two bounds.

    Args:
        min_sec (int): Minimum interval in seconds.
        max_sec (int): Maximum interval in seconds.

    Returns:
        int: Random interval in seconds.
    """
    return random.randint(min_sec, max_sec)

def run_rotation_loop():
    """
    Main loop that rotates IPs at randomized intervals.
    """
    config = load_ip_pool()
    
    ip_list = config.get("ip_pool", [])
    interface = config.get("network_interface", "eth0")
    interval_range = config.get("rotation_interval", {"min": 300, "max": 600})

    if len(ip_list) < 2:
        logging.warning("IP pool must contain at least 2 IPs to rotate.")
        return

    logging.info("Starting IP rotation scheduler...")
    current_ip = ip_list[0]  # Start with the first IP

    while True:
        # Pick a new IP different from the current one
        new_ip = random.choice([ip for ip in ip_list if ip != current_ip])

        logging.info(f"[ROTATE] {current_ip} -> {new_ip} on interface {interface}")
        success = rotate_ip(old_ip=current_ip, new_ip=new_ip, interface=interface)

        if success:
            current_ip = new_ip
        else:
            logging.warning(f"Rotation failed from {current_ip} to {new_ip}")

        # Wait for a jittered/random interval before next rotation
        wait_time = jittered_interval(interval_range["min"], interval_range["max"])
        logging.info(f"Next rotation in {wait_time} seconds...")
        time.sleep(wait_time)

if __name__ == "__main__":
    run_rotation_loop()
