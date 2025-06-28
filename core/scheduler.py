"""
Module: core/scheduler.py

Purpose:
Controls timed rotation of IP addresses using jittered/random scheduling.
Loads IP pool from config, selects new IPs, and invokes the IP rotation logic.
Can be extended to integrate with DNS, logging services, and decoy infrastructure.
"""

# core/scheduler.py

import time
import random
import logging
import yaml
from datetime import datetime
from core.ip_manager import rotate_ip
from core.tls_manager import rotate_tls_cert

cert_path, key_path = rotate_tls_cert(label="rotated_tls", cn="myserver.local")


# ---------------------------
# Load Configuration
# ---------------------------
def load_config(path="config/default_config.yaml"):
    with open(path, "r") as file:
        return yaml.safe_load(file)

# ---------------------------
# Setup Logging
# ---------------------------
def setup_logger():
    logging.basicConfig(
        filename="logs/rotation.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

# ---------------------------
# Pick Next IP Address
# ---------------------------
def choose_new_ip(ip_pool, current_ip):
    candidates = [ip for ip in ip_pool if ip != current_ip]
    return random.choice(candidates) if candidates else current_ip

# ---------------------------
# Rotation Task
# ---------------------------
def perform_rotation(config, current_ip):
    ip_pool = config["rotation"]["ip_pool"]
    interface = config["rotation"]["interface"]

    new_ip = choose_new_ip(ip_pool, current_ip)
    success = rotate_ip(current_ip, new_ip, interface)

    if success:
        logging.info(f"IP rotation successful: {current_ip} ➜ {new_ip}")
        return new_ip
    else:
        logging.warning("IP rotation failed.")
        return current_ip

# ---------------------------
# Main Scheduler Logic
# ---------------------------
def start_scheduler():
    setup_logger()
    config = load_config()
    base_interval = config["rotation"]["base_interval"]
    jitter_range = config["rotation"]["jitter_range"]
    ip_pool = config["rotation"]["ip_pool"]
    current_ip = ip_pool[0]  # Starting IP

    logging.info("Scheduler started.")

    while True:
        # Perform IP rotation
        current_ip = perform_rotation(config, current_ip)

        # Calculate next wait time with jitter
        jitter = random.randint(-jitter_range, jitter_range)
        wait_time = max(10, base_interval + jitter)  # Avoid negative or too short intervals

        logging.info(f"Next rotation in {wait_time} seconds")
        time.sleep(wait_time)

# ---------------------------
# Entry Point
# ---------------------------
if __name__ == "__main__":
    try:
        scheduler_loop()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user.")
