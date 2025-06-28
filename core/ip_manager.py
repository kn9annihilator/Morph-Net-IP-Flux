"""
Module: core/ip_manager.py

Purpose:
Handles dynamic IP assignment and removal for Moving Target Defense (MTD) 
by invoking platform-agnostic shell scripts. Ensures logging and interface detection.
"""

import subprocess
import logging
import os
import psutil
from datetime import datetime

# ---------------------------
# Path Setup (POSIX-compliant)
# ---------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL_DIR = os.path.join(BASE_DIR, "shell").replace("\\", "/")  # Safe for Bash
LOG_DIR = os.path.join(BASE_DIR, "logs").replace("\\", "/")

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "rotation.log")

# ---------------------------
# Logging Configuration
# ---------------------------
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------
# Interface Detection
# ---------------------------
def detect_interface() -> str:
    """
    Auto-detects the first non-loopback interface (e.g., eth0, ens33).
    Returns:
        str: Detected interface name.
    """
    interfaces = psutil.net_if_addrs().keys()
    for iface in interfaces:
        if iface != "lo":
            return iface
    return "eth0"

# ---------------------------
# Assign IP
# ---------------------------
def assign_ip(ip_address: str, interface: str = None) -> bool:
    """
    Assigns a new IP to the specified interface using shell script.
    """
    interface = interface or detect_interface()
    script_path = os.path.join(SHELL_DIR, "assign_ip.sh").replace("\\", "/")

    try:
        result = subprocess.run(
            ["bash", script_path, ip_address, interface],
            check=True, capture_output=True, text=True
        )
        logging.info(f"[ASSIGN] IP {ip_address} assigned to {interface}")
        logging.debug(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"[ASSIGN] Failed to assign IP {ip_address}: {e.stderr}")
        return False
    except FileNotFoundError:
        logging.critical(f"[ASSIGN] Script not found: {script_path}")
        return False

# ---------------------------
# Flush IP
# ---------------------------
def flush_ip(ip_address: str, interface: str = None) -> bool:
    """
    Removes an IP from the interface using shell script.
    """
    interface = interface or detect_interface()
    script_path = os.path.join(SHELL_DIR, "flush_ip.sh").replace("\\", "/")

    try:
        result = subprocess.run(
            ["bash", script_path, ip_address, interface],
            check=True, capture_output=True, text=True
        )
        logging.info(f"[FLUSH] IP {ip_address} flushed from {interface}")
        logging.debug(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"[FLUSH] Failed to flush IP {ip_address}: {e.stderr}")
        return False
    except FileNotFoundError:
        logging.critical(f"[FLUSH] Script not found: {script_path}")
        return False

# ---------------------------
# Rotate IP
# ---------------------------
def rotate_ip(old_ip: str, new_ip: str, interface: str = None) -> bool:
    """
    Atomically rotates IP: flushes old and assigns new.
    """
    interface = interface or detect_interface()
    logging.info(f"[ROTATE] Starting rotation: {old_ip} → {new_ip} on {interface}")
    
    flushed = flush_ip(old_ip, interface)
    assigned = assign_ip(new_ip, interface)

    if flushed and assigned:
        logging.info(f"[ROTATE] Successfully rotated IP from {old_ip} to {new_ip}")
        return True
    else:
        logging.error(f"[ROTATE] IP rotation failed: {old_ip} → {new_ip}")
        return False

# ---------------------------
# Manual Test Execution
# ---------------------------
if __name__ == "__main__":
    # ⚠️ Replace these with safe dummy IPs in your local testbed
    success = rotate_ip("192.168.1.100", "192.168.1.101")
    print("IP rotation succeeded." if success else "IP rotation failed.")
