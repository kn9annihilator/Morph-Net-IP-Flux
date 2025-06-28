 # core/dns_controller.py

import requests
import yaml
import logging
from datetime import datetime

# ---------------------------
# Load DNS Config
# ---------------------------
def load_dns_config(config_path="config/default_config.yaml"):
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
    return config.get("dns", {})

# ---------------------------
# Setup Logger
# ---------------------------
def setup_logger():
    logging.basicConfig(
        filename="logs/rotation.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

# ---------------------------
# Update DNS Record (Cloudflare)
# ---------------------------
def update_cloudflare_dns(zone_id, api_token, record_name, new_ip, ttl):
    # Step 1: Get the DNS record ID
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    params = {"type": "A", "name": record_name}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if not data.get("success", False):
        logging.error("Failed to fetch DNS record ID.")
        return False

    try:
        record_id = data["result"][0]["id"]
    except (IndexError, KeyError):
        logging.error("DNS record not found for update.")
        return False

    # Step 2: Update the A record to the new IP
    update_url = f"{url}/{record_id}"
    payload = {
        "type": "A",
        "name": record_name,
        "content": new_ip,
        "ttl": ttl,
        "proxied": False
    }

    update_resp = requests.put(update_url, headers=headers, json=payload)
    update_data = update_resp.json()

    if update_data.get("success"):
        logging.info(f"DNS record updated: {record_name} ➜ {new_ip}")
        return True
    else:
        logging.error("DNS update failed.")
        return False

# ---------------------------
# Public Function to Rotate DNS
# ---------------------------
def update_dns_record(new_ip, config_path="config/default_config.yaml"):
    setup_logger()
    dns_config = load_dns_config(config_path)

    zone_id = dns_config.get("zone_id")
    api_token = dns_config.get("api_token")
    record_name = dns_config.get("record_name")
    ttl = dns_config.get("ttl", 60)

    if not all([zone_id, api_token, record_name]):
        logging.error("Missing DNS config fields.")
        return False

    return update_cloudflare_dns(zone_id, api_token, record_name, new_ip, ttl)

# ---------------------------
# For Direct Testing
# ---------------------------
if __name__ == "__main__":
    test_ip = "192.168.56.102"
    result = rotate_dns_record(test_ip)
    print("Complete Success " if result else "Failed")

