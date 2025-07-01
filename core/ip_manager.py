# core/ip_manager.py

"""
Handles IP assignment and flushing on a network interface
for Moving Target Defense, via shell scripts.
"""

import os
import subprocess
import logging
from core.dns_controller import update_dns_record


# ---------------------------
# Setup Constants
# ---------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL_DIR = os.path.join(BASE_DIR, "shell")
LOG_FILE = os.path.join(BASE_DIR, "logs", "rotation.log")

# ---------------------------
# Setup Logging
# ---------------------------

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------
# IP Assign Function
# ---------------------------

def assign_ip(ip_address: str, interface: str = "eth0") -> bool:
    """
    Assigns a new IP to a given network interface using shell script.
    """
    script_path = os.path.join(SHELL_DIR, "assign_ip.sh").replace("\\", "/")
    if script_path[1:3] == ":/":  # e.g., D:/...
        script_path = f"/mnt/{script_path[0].lower()}{script_path[2:]}"



    try:
        subprocess.run(["bash", script_path, ip_address, interface], check=True)
        logging.info(f"Assigned IP {ip_address} to interface {interface}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to assign IP {ip_address} to {interface}: {str(e)}")
        return False

# ---------------------------
# IP Flush Function
# ---------------------------

def flush_ip(ip_address: str, interface: str = "eth0") -> bool:
    """
    Flushes/removes an IP from the given network interface using shell script.
    Uses WSL-safe paths for Git Bash/Windows compatibility.
    """
    script_path = os.path.join(SHELL_DIR, "flush_ip.sh")
    script_path = os.path.abspath(script_path).replace("\\", "/")

    # Convert Windows path to WSL-style if needed
    if script_path[1:3] == ":/":
        drive_letter = script_path[0].lower()
        script_path = f"/mnt/{drive_letter}{script_path[2:]}"

    try:
        result = subprocess.run(
            ["bash", script_path, ip_address, interface],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        logging.info(f"Flushed IP {ip_address} from interface {interface}")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Flush IP stderr: {e.stderr.decode().strip()}")
        logging.error(f"Failed to flush IP {ip_address} from {interface}: {str(e)}")
        return False


# ---------------------------
# Rotate IP (Flush + Assign)
# ---------------------------

def rotate_ip(old_ip: str, new_ip: str, interface: str = "eth0") -> bool:
    """
    Flushes old IP and assigns new IP atomically.
    """
    logging.info(f"Rotating IP: {old_ip} → {new_ip}")
    flushed = flush_ip(old_ip, interface)
    assigned = assign_ip(new_ip, interface)

    if flushed and assigned:
        logging.info(f"IP rotation successful: {old_ip} → {new_ip}")
        update_dns_record(new_ip)
        return True

    else:
        logging.error(f"IP rotation failed: {old_ip} → {new_ip}")
        return False

# ---------------------------
# Test Run
# ---------------------------

if __name__ == "__main__":
    success = rotate_ip("192.168.1.100", "192.168.1.101")
    if success:
        print("IP rotation succeeded.")
    else:
        print("IP rotation failed.")
