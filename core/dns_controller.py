# core/dns_controller.py

import requests
import logging

def _get_record_id(zone_id: str, api_token: str, record_name: str) -> str | None:
    """Fetches the ID for a given DNS record name."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    params = {"type": "A", "name": record_name}

    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("success") and data.get("result"):
            return data["result"][0]["id"]
        else:
            logging.error(f"Could not find DNS record for {record_name}. Response: {data.get('errors')}")
            return None
    except requests.RequestException as e:
        logging.error(f"Failed to fetch DNS record ID from Cloudflare: {e}")
        return None

def update_dns_record(config: dict, new_ip: str) -> bool:
    """Updates a Cloudflare DNS A record using settings from the config."""
    dns_config = config.get("dns", {})
    api_token = dns_config.get("api_token")
    zone_id = dns_config.get("zone_id")
    record_name = dns_config.get("record_name")
    proxied = dns_config.get("proxied", False)
    ttl = dns_config.get("ttl", 60)

    if not all([api_token, zone_id, record_name]):
        logging.error("Missing critical DNS configuration (API token, zone ID, or record name).")
        return False

    # This is a good place to check if the API token is still the default placeholder
    if not api_token or "YOUR_CLOUDFLARE_API_TOKEN" in api_token:
        logging.warning("[SIMULATING] DNS update because API token is not set.")
        logging.info(f"[OK] Simulated DNS update: {record_name} -> {new_ip}")
        return True

    record_id = _get_record_id(zone_id, api_token, record_name)
    if not record_id:
        return False

    update_url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records/{record_id}"
    headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}
    payload = {
        "type": "A",
        "name": record_name,
        "content": new_ip,
        "ttl": ttl,
        "proxied": proxied
    }

    try:
        response = requests.put(update_url, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            logging.info(f"[OK] Successfully updated DNS record: {record_name} -> {new_ip}")
            return True
        else:
            logging.error(f"DNS update failed. Response: {data.get('errors')}")
            return False
    except requests.RequestException as e:
        logging.error(f"Failed to send DNS update request to Cloudflare: {e}")
        return False