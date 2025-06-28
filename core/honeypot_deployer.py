 # core/honeypot_deployer.py

import socket
import threading
import json
import os
import random
import time
from datetime import datetime

# ---------------------------
# Configuration
# ---------------------------

HTTP_PORT_RANGE = (8000, 9000)
SSH_PORT_RANGE = (2200, 2300)
LOG_FILE = "logs/honeypot_hits.json"

# ---------------------------
# Port Generator
# ---------------------------

def get_random_port(port_range):
    """
    Get a random available port within a given range.
    """
    while True:
        port = random.randint(*port_range)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(("0.0.0.0", port))
                return port
            except OSError:
                continue  # Try another port if unavailable

# ---------------------------
# Logging Function
# ---------------------------

def log_event(service_type, client_ip, client_port, decoy_port):
    """
    Log a honeypot hit with timestamp, IP, and port.
    """
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "service": service_type,
        "source_ip": client_ip,
        "source_port": client_port,
        "decoy_port": decoy_port
    }

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.isfile(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f, indent=2)

    with open(LOG_FILE, "r+") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            data = []
        data.append(log_entry)
        f.seek(0)
        json.dump(data, f, indent=2)

# ---------------------------
# Fake HTTP Server
# ---------------------------

def start_fake_http_server(port):
    """
    Starts a fake HTTP server that accepts any request and returns a generic response.
    """
    def handler(conn, addr):
        try:
            request = conn.recv(1024).decode(errors="ignore")
            log_event("HTTP", addr[0], addr[1], port)
            response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nWelcome to MorphNetIPFlux."
            conn.sendall(response)
        except Exception:
            pass
        finally:
            conn.close()

    def server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
            s.listen(5)
            print(f"[HTTP] Honeypot listening on port {port}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handler, args=(conn, addr), daemon=True).start()

    threading.Thread(target=server, daemon=True).start()

# ---------------------------
# Fake SSH Server
# ---------------------------

def start_fake_ssh_server(port):
    """
    Starts a fake SSH server that sends a fake SSH banner and closes connection.
    """
    def handler(conn, addr):
        try:
            conn.sendall(b"SSH-2.0-OpenSSH_7.9p1 Debian-10\r\n")
            log_event("SSH", addr[0], addr[1], port)
        except Exception:
            pass
        finally:
            conn.close()

    def server():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
            s.listen(5)
            print(f"[SSH] Honeypot listening on port {port}")
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handler, args=(conn, addr), daemon=True).start()

    threading.Thread(target=server, daemon=True).start()

# ---------------------------
# Entrypoint
# ---------------------------

def launch_honeypots():
    """
    Launches fake HTTP and SSH servers on random decoy ports.
    """
    http_port = get_random_port(HTTP_PORT_RANGE)
    ssh_port = get_random_port(SSH_PORT_RANGE)

    start_fake_http_server(http_port)
    start_fake_ssh_server(ssh_port)

    # Keep the script alive (in real deploy, use a process manager)
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("Honeypots terminated.")

# ---------------------------
# CLI Entry
# ---------------------------

if __name__ == "__main__":
    launch_honeypots()

