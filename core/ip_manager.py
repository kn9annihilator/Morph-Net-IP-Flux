# core/ip_manager.py

import os
import subprocess
import logging
import time

# ==============================================================================
# DEVELOPMENT & DEPLOYMENT MODE SWITCH
# ------------------------------------------------------------------------------
# Set to "production" when deploying on a Linux server.
# Set to "simulation" for local development on Windows/macOS.
# ==============================================================================
DEVELOPMENT_MODE = "simulation" # Options: "production", "simulation"


# ==============================================================================
# SECTION 1: PRODUCTION CODE
# This is the real implementation for a Linux server environment.
# It requires administrator privileges to run correctly.
# ==============================================================================

def _production_run_script(script_name: str, *args) -> bool:
    """A robust helper to run a shell script and handle its output."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.abspath(os.path.join(current_dir, '..', 'shell', script_name))
        
        # This conversion is for Windows + Git Bash compatibility if needed
        if os.name == 'nt':
            if len(script_path) > 2 and script_path[1] == ':':
                drive = script_path[0].lower()
                rest_of_path = script_path[2:].replace('\\', '/')
                script_path = f"/mnt/{drive}{rest_of_path}"
        
        cmd = ["bash", script_path, *args]
        result = subprocess.run(
            cmd, check=True, capture_output=True, text=True, timeout=30
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

def _production_rotate_ip(old_ip: str, new_ip: str, interface: str, subnet_mask: str) -> bool:
    """Production logic for IP rotation with rollback."""
    logging.info(f"--- Starting IP Rotation: {old_ip} -> {new_ip} ---")

    if not _production_run_script("flush_ip.sh", old_ip, interface, subnet_mask):
        logging.error("Rotation failed at 'flush' step. Aborting.")
        return False

    if _production_run_script("assign_ip.sh", new_ip, interface, subnet_mask):
        logging.info(f"--- [OK] IP Rotation successful. New IP is {new_ip} ---")
        return True
    else:
        logging.error("Rotation failed at 'assign' step. Initiating rollback...")
        if _production_run_script("assign_ip.sh", old_ip, interface, subnet_mask):
            logging.warning(f"[OK] Rollback successful. Server is back on the old IP: {old_ip}.")
        else:
            logging.critical(f"[!] CRITICAL: Rollback FAILED. Network interface may be unconfigured!")
        return False

# ==============================================================================
# SECTION 2: SIMULATION CODE
# This is for local development on machines that can't run the network commands.
# It pretends to succeed, allowing testing of the full MTD cycle.
# ==============================================================================

def _simulation_rotate_ip(old_ip: str, new_ip: str, interface: str, subnet_mask: str) -> bool:
    """Simulates a successful IP rotation for development and demo purposes."""
    logging.info(f"--- [SIMULATION MODE] Starting IP Rotation: {old_ip} -> {new_ip} ---")
    
    logging.info(f"[SIMULATING] Flush IP {old_ip} on interface {interface}...")
    time.sleep(0.2)
    logging.info(f"[OK] Simulated Flush of IP {old_ip}.")
    
    logging.info(f"[SIMULATING] Assign IP {new_ip} on interface {interface}...")
    time.sleep(0.2)
    logging.info(f"[OK] Simulated Assign of IP {new_ip}.")
    
    logging.info(f"--- [OK] Simulated IP Rotation successful. New IP is {new_ip} ---")
    return True

# ==============================================================================
# SECTION 3: PUBLIC FUNCTION
# This is the only function that other modules should call.
# It will automatically use the correct version based on the DEVELOPMENT_MODE flag.
# ==============================================================================

def rotate_ip(old_ip: str, new_ip: str, interface: str, subnet_mask: str) -> bool:
    """
    Public function to rotate an IP. Dispatches to either the production or
    simulation function based on the DEVELOPMENT_MODE flag at the top of the file.
    """
    if DEVELOPMENT_MODE == "production":
        return _production_rotate_ip(old_ip, new_ip, interface, subnet_mask)
    else: # Default to simulation
        return _simulation_rotate_ip(old_ip, new_ip, interface, subnet_mask)