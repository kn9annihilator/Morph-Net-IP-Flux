# core/honeypot_deployer.py

import socket
import threading
import json
import os
import random
import logging
from datetime import datetime

# A lock to prevent race conditions when writing to the log file
log_lock = threading.Lock()

def log_event(service_type: str, client_ip: str, client_port: int, decoy_port: int):
    """Logs a honeypot hit to a JSON file in a thread-safe manner."""
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": service_type,
        "source_ip": client_ip,
        "source_port": client_port,
        "decoy_port": decoy_port
    }
    
    log_file = "logs/honeypot_hits.json"
    
    # Use a lock to ensure only one thread can write to the file at a time
    with log_lock:
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # Read existing data
            if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
                with open(log_file, "r") as f:
                    data = json.load(f)
            else:
                data = []
            
            # Append new entry and write back
            data.append(log_entry)
            with open(log_file, "w") as f:
                json.dump(data, f, indent=2)
                
        except (IOError, json.JSONDecodeError) as e:
            logging.error(f"Error writing to honeypot log: {e}")

def _start_decoy_server(port: int, service_type: str, banner: bytes):
    """A generic handler to start a decoy TCP server on a given port."""
    def handler(conn, addr):
        try:
            log_event(service_type, addr[0], addr[1], port)
            conn.sendall(banner)
        except socket.error as e:
            logging.debug(f"Socket error on {service_type} honeypot: {e}")
        finally:
            conn.close()

    def server_loop():
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(("0.0.0.0", port))
                s.listen(5)
                logging.info(f"[{service_type}] Honeypot now listening on port {port}")
                while True:
                    conn, addr = s.accept()
                    threading.Thread(target=handler, args=(conn, addr), daemon=True).start()
        except OSError as e:
            logging.error(f"Failed to bind {service_type} honeypot to port {port}: {e}")

    # Start the server loop in a background thread
    threading.Thread(target=server_loop, daemon=True).start()

def launch_honeypots(config: dict):
    """
    Launches fake HTTP and SSH servers on random decoy ports.
    This function is non-blocking.
    """
    honeypot_config = config.get("honeypot", {})
    http_range = honeypot_config.get("http_range", [8000, 9000])
    ssh_range = honeypot_config.get("ssh_range", [2000, 3000])

    # Get random ports for the decoys
    http_port = random.randint(*http_range)
    ssh_port = random.randint(*ssh_range)

    # Define banners
    http_banner = b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n<h1>Welcome</h1>"
    ssh_banner = b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1\r\n"

    # Launch servers
    _start_decoy_server(http_port, "HTTP", http_banner)
    _start_decoy_server(ssh_port, "SSH", ssh_banner)
    
    logging.info("Honeypot services launched in background.")