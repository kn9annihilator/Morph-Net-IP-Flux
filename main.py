# main.py

import os
import yaml
import dotenv
import threading
import time

# Import project modules
from core.ip_manager import rotate_ip
from core.scheduler import start_scheduler
from core.dns_controller import update_dns_record
from core.honeypot_deployer import launch_honeypots

# -----------------------------
# Step 1: Load Configurations
# -----------------------------

def load_config():
    """
    Load configuration from YAML and environment files.
    """
    config_path = "config/default_config.yaml"
    env_path = "config/secrets.env"

    # Load environment variables
    if os.path.exists(env_path):
        dotenv.load_dotenv(env_path)

    # Load YAML config
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config

# -----------------------------
# Step 2: Start Core Services
# -----------------------------

def init_ip_rotation(config):
    """
    Initialize IP rotation logic using config.
    """
    old_ip = config.get("ip_rotation", {}).get("old_ip", "192.168.1.100")
    new_ip = config.get("ip_rotation", {}).get("new_ip", "192.168.1.101")
    print(f"[+] Rotating IP from {old_ip} to {new_ip}...")
    success = rotate_ip(old_ip, new_ip)
    if success:
        print("[✓] IP Rotation successful.")
    else:
        print("[!] IP Rotation failed.")

def init_dns_update(config):
    """
    Trigger DNS update (stub logic).
    """
    domain = config.get("dns", {}).get("domain", "example.com")
    new_ip = config.get("ip_rotation", {}).get("new_ip", "192.168.1.101")
    ttl = config.get("dns", {}).get("ttl", 60)
    update_dns_record(new_ip)
    print(f"[✓] DNS record updated for {domain} -> {new_ip}")

def init_scheduler():
    """
    Starts the system scheduler in a background thread.
    """
    print("[~] Launching scheduler...")
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()
    print("[✓] Scheduler running in background.")

def init_honeypots():
    """
    Start honeypot services for HTTP and SSH decoys.
    """
    print("[~] Deploying honeypots...")
    honeypot_thread = threading.Thread(target=launch_honeypots, daemon=True)
    honeypot_thread.start()
    print("[✓] Honeypots running in background.")

# -----------------------------
# Entrypoint
# -----------------------------

def main():
    print("\n[+] Morph Net IP Flux — Dynamic Defense Engine Starting...\n")

    try:
        config = load_config()

        # Initialize components
        init_ip_rotation(config)
        init_dns_update(config)
        init_honeypots()
        init_scheduler()

        # Keep the main process alive
        print("[✓] All services initialized. Monitoring in progress...\n")
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n[!] Shutdown signal received. Exiting gracefully...\n")

    except Exception as e:
        print(f"[X] Fatal error occurred: {e}\n")

if __name__ == "__main__":
    main()
