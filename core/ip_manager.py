"""
Module: core/ip_manager.py

Purpose:
Handles the assignment and removal of IP addresses on the system's network interface
by interacting with shell scripts and managing stateful logs. It is responsible for
initiating IP changes as part of the broader Moving Target Defense (MTD) strategy.
"""

import subprocess
import logging
import os
import sys
from datetime import datetime

# Load configuration paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHELL_DIR = os.path.join(BASE_DIR, "shell")
LOG_FILE = os.path.join(BASE_DIR, "logs", "rotation.log")

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def assign_ip(ip_address: str, interface: str = "eth0") -> bool:
    """
    Assigns a new IP address to the specified network interface using shell script.
    
    Args:
        ip_address (str): IP address to assign.
        interface (str): Network interface (default is eth0).

    Returns:
        bool: True if successful, False otherwise.
    """
    script_path = os.path.join(SHELL_DIR, "assign_ip.sh")
    try:
        result = subprocess.run(["bash", script_path, ip_address, interface], check=True)
        logging.info(f"Assigned IP {ip_address} to interface {interface}.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to assign IP {ip_address}: {str(e)}")
        return False

def flush_ip(ip_address: str, interface: str = "eth0") -> bool:
    """
    Removes the given IP address from the network interface.

    Args:
        ip_address (str): IP address to remove.
        interface (str): Network interface (default is eth0).

    Returns:
        bool: True if successful, False otherwise.
    """
    script_path = os.path.join(SHELL_DIR, "flush_ip.sh")
    try:
        result = subprocess.run(["bash", script_path, ip_address, interface], check=True)
        logging.info(f"Flushed IP {ip_address} from interface {interface}.")
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to flush IP {ip_address}: {str(e)}")
        return False

def rotate_ip(old_ip: str, new_ip: str, interface: str = "eth0") -> bool:
    """
    Atomically rotates the IP from old to new.

    Args:
        old_ip (str): IP to remove.
        new_ip (str): IP to assign.
        interface (str): Network interface.

    Returns:
        bool: True if both flush and assign succeed.
    """
    logging.info(f"Rotating IP: Removing {old_ip}, Assigning {new_ip}")
    flushed = flush_ip(old_ip, interface)
    assigned = assign_ip(new_ip, interface)
    if flushed and assigned:
        logging.info(f"Successfully rotated IP from {old_ip} to {new_ip}.")
        return True
    else:
        logging.error(f"IP rotation failed: {old_ip} -> {new_ip}")
        return False

if __name__ == "__main__":
    # Simple test run when executing the module directly
    # Replace these IPs with dummy/test IPs as needed
    success = rotate_ip("192.168.1.100", "192.168.1.101")
    if success:
        print("IP rotation succeeded.")
    else:
        print("IP rotation failed.")

