# core/scheduler.py
from core.status_manager import update_status
import time
import random
import logging
import threading


# We will import these functions, which will be refactored later
from core.ip_manager import rotate_ip
from core.dns_controller import update_dns_record
from core.tls_manager import rotate_tls_cert

def _perform_full_rotation(config: dict, current_ip: str) -> str:
    """
    Performs the full MTD rotation cycle: IP -> DNS -> TLS.
    Returns the new IP on success, or the old IP on failure.
    """
    rotation_config = config.get("rotation", {})
    ip_pool = rotation_config.get("ip_pool", [])
    interface = rotation_config.get("interface", "eth0")
    subnet_mask = rotation_config.get("subnet_mask", "/24")
    
    # 1. Choose a new IP different from the current one
    candidates = [ip for ip in ip_pool if ip != current_ip]
    if not candidates:
        logging.warning("No available IPs to rotate to. Skipping rotation cycle.")
        return current_ip
    new_ip = random.choice(candidates)

    # 2. Rotate the IP address. This is the most critical step.
    if rotate_ip(current_ip, new_ip, interface, subnet_mask):
        logging.info(f"IP rotation successful. New active IP is {new_ip}.")
        
        # 3. Update DNS record to point to the new IP.
        # This now happens ONLY after a successful IP rotation.
        logging.info(f"Updating DNS record for {config['dns']['record_name']} to point to {new_ip}...")
        update_dns_record(config, new_ip) # We will refactor this function next
        
        # 4. Rotate TLS certificate to de-correlate identity
        logging.info("Rotating TLS certificate...")
        rotate_tls_cert(config) # We will refactor this function next
        
        # Return the new IP as the new current state
        return new_ip
    else:
        # If rotate_ip failed, it already logged the error and attempted a rollback.
        # We return the old IP to signify that the state has not changed.
        logging.error("IP rotation failed. System state remains on the old IP.")
        return current_ip

# In core/scheduler.py

def scheduler_loop(config: dict):
    """The main scheduler loop that triggers MTD cycles."""
    rotation_config = config.get("rotation", {})
    base_interval = rotation_config.get("base_interval", 300)
    jitter_range = rotation_config.get("jitter_range", 60)

    current_ip = rotation_config.get("ip_pool", ["127.0.0.1"])[0]
    logging.info(f"Scheduler started. Initial IP is assumed to be {current_ip}.")

    # Initial status update
    total_rotations = 0
    update_status({
        "status": "Running",
        "mode": "simulation", # Assuming simulation mode for now
        "current_ip": current_ip,
        "next_rotation_in": "Starting cycle...",
        "total_rotations": total_rotations
    })

    while True:
        # Perform the full rotation logic
        new_ip = _perform_full_rotation(config, current_ip)
        if new_ip != current_ip:
            current_ip = new_ip
            total_rotations += 1

        # Calculate the next wait time with jitter
        jitter = random.randint(-jitter_range, jitter_range)
        wait_time = max(10, base_interval + jitter)
        logging.info(f"--- Next rotation cycle in {wait_time} seconds ---")

        # Update status before sleeping
        update_status({
            "status": "Waiting",
            "mode": "simulation",
            "current_ip": current_ip,
            "next_rotation_in": f"{wait_time}s",
            "total_rotations": total_rotations
        })

        time.sleep(wait_time)
def start_scheduler(config: dict):
    """Starts the scheduler loop in a non-blocking background thread."""
    logging.info("Initializing scheduler thread...")
    thread = threading.Thread(target=scheduler_loop, args=(config,), daemon=True)
    thread.start()
    logging.info("Scheduler is running in the background.")