# core/ip_manager.py

import os
import subprocess
import logging

def _to_wsl_path(path: str) -> str:
    """Converts a Windows path to a WSL-compatible path if necessary."""
    if os.name == 'nt' and len(path) > 2 and path[1] == ':':
        drive = path[0].lower()
        rest_of_path = path[2:].replace('\\', '/')
        return f"/mnt/{drive}{rest_of_path}"
    return path.replace("\\", "/")

def _run_script(script_name: str, *args) -> bool:
    """A robust helper to run a shell script and handle its output."""
    try:
        # --- THIS IS THE CORRECTED PATH LOGIC ---
        # Get the directory of the current Python script (core/)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build the path to the shell script
        script_path = os.path.join(current_dir, '..', 'shell', script_name)
        # Use os.path.abspath to resolve the '..' and create a clean, absolute path
        script_path = os.path.abspath(script_path)
        # --- END OF CORRECTION ---

        # Now convert the clean, absolute path for WSL
        script_path = _to_wsl_path(script_path)
        
        cmd = ["bash", script_path, *args]
        result = subprocess.run(
            cmd, 
            check=True, 
            capture_output=True, 
            text=True,
            timeout=30
        )
        if result.stdout:
            logging.info(f"Output from {script_name}: {result.stdout.strip()}")
        return True
    except subprocess.TimeoutExpired:
        logging.error(f"Execution of {script_name} timed out.")
        return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing {script_name}. Stderr: {e.stderr.strip()}")
        return False

def assign_ip(ip_address: str, interface: str, subnet_mask: str) -> bool:
    """Assigns a new IP to a given network interface."""
    logging.info(f"[IP] Attempting to assign IP {ip_address} to interface {interface}...")
    success = _run_script("assign_ip.sh", ip_address, interface, subnet_mask)
    if success:
        logging.info(f"[OK] Successfully assigned IP {ip_address}.")
    else:
        logging.error(f"[!] Failed to assign IP {ip_address}.")
    return success

def flush_ip(ip_address: str, interface: str, subnet_mask: str) -> bool:
    """Flushes an IP from the given network interface."""
    logging.info(f"[IP] Attempting to flush IP {ip_address} from interface {interface}...")
    success = _run_script("flush_ip.sh", ip_address, interface, subnet_mask)
    if success:
        logging.info(f"[OK] Successfully flushed IP {ip_address}.")
    else:
        logging.error(f"[!] Failed to flush IP {ip_address}.")
    return success

def rotate_ip(old_ip: str, new_ip: str, interface: str, subnet_mask: str) -> bool:
    """
    Atomically rotates the IP by flushing the old and assigning the new.
    Includes rollback logic for enhanced reliability.
    """
    logging.info(f"--- Starting IP Rotation: {old_ip} -> {new_ip} ---")

    if not flush_ip(old_ip, interface, subnet_mask):
        logging.error("Rotation failed at 'flush' step. Aborting.")
        return False

    if assign_ip(new_ip, interface, subnet_mask):
        logging.info(f"--- [OK] IP Rotation successful. New IP is {new_ip} ---")
        return True
    else:
        logging.error("Rotation failed at 'assign' step. Initiating rollback...")
        if assign_ip(old_ip, interface, subnet_mask):
            logging.warning(f"[OK] Rollback successful. Server is back on the old IP: {old_ip}.")
        else:
            logging.critical(f"[!] CRITICAL: Rollback FAILED. Network interface may be unconfigured!")
        return False