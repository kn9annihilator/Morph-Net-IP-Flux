"""
Module: core/scheduler.py

Purpose:
Controls timed rotation of IP addresses using jittered/random scheduling.
Loads IP pool from config, selects new IPs, and invokes the IP rotation logic.
Can be extended to integrate with DNS, logging services, and decoy infrastructure.
"""

import time
import random
import logging
import yaml
from datetime import datetime
from core.ip_manager import rotate_ip
from core.tls_manager import rotate_tls_cert


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
# Main Scheduler Loop
# ---------------------------
def scheduler_loop():
    setup_logger()
    config = load_config()
    base_interval = config["rotation"]["base_interval"]
    jitter_range = config["rotation"]["jitter_range"]
    ip_pool = config["rotation"]["ip_pool"]
    current_ip = ip_pool[0]  # Starting IP

    logging.info("Scheduler started.")

    # Rotate TLS cert at startup
    try:
        cert_path, key_path = rotate_tls_cert()
        logging.info(f"TLS certificate rotated at startup. Paths: {cert_path}, {key_path}")
    except Exception as e:
        logging.error(f"Failed to rotate TLS certificate at startup: {e}")

    while True:
        current_ip = perform_rotation(config, current_ip)

        jitter = random.randint(-jitter_range, jitter_range)
        wait_time = max(10, base_interval + jitter)
        logging.info(f"Next rotation in {wait_time} seconds")
        time.sleep(wait_time)

# ---------------------------
# Start in Thread (for main.py)
# ---------------------------
def start_scheduler():
    import threading
    thread = threading.Thread(target=scheduler_loop, daemon=True)
    thread.start()

# ---------------------------
# Entry Point (for testing only)
# ---------------------------
if __name__ == "__main__":
    try:
        scheduler_loop()
    except KeyboardInterrupt:
        logging.info("Scheduler stopped by user.")
