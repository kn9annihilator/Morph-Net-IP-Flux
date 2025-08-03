# core/honeypot_deployer.py

import socket
import threading
import json
import os
import random
import logging
from datetime import datetime

# --- Global Threading Lock ---
# When multiple attackers connect at the same time, each connection is handled
# in a separate thread. If two threads try to write to the log file simultaneously,
# they can corrupt the file. A 'Lock' is a simple mechanism that ensures only
# one thread can execute the "critical section" of code (writing to the file) at a time.
log_lock = threading.Lock()

# --- Thread-Safe Logging Function ---
def log_event(service_type: str, client_ip: str, client_port: int, decoy_port: int):
    """
    Logs a honeypot connection event to a JSON file. This function is designed
    to be "thread-safe," meaning it can be called from multiple threads at once
    without corrupting the log file.
    """
    # Create a dictionary to hold the details of the connection event.
    # Using a structured format like JSON makes the logs easy to parse later.
    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z", # Use ISO 8601 format with UTC timezone
        "service": service_type,
        "source_ip": client_ip,
        "source_port": client_port,
        "decoy_port": decoy_port,
        "notes": "Attacker interaction detected on decoy port."
    }
    
    log_file = "logs/honeypot_hits.json"
    
    # The 'with' statement is the modern way to use a lock. It automatically
    # acquires the lock when entering the block and releases it when exiting,
    # even if an error occurs inside. This is safer than manually calling lock.acquire()
    # and lock.release().
    with log_lock:
        try:
            # Ensure the 'logs' directory exists before trying to write to it.
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            
            # To append to a JSON file, we must read the existing content,
            # add our new entry to the list, and then write the whole list back.
            if os.path.exists(log_file) and os.path.getsize(log_file) > 0:
                with open(log_file, "r") as f:
                    # It's possible the file exists but is empty or corrupt.
                    # A try-except block handles this gracefully.
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = [] # If file is corrupt, start with a fresh list
            else:
                data = [] # If file doesn't exist, start with an empty list
            
            # Add the new log entry.
            data.append(log_entry)
            
            # Write the updated list back to the file.
            with open(log_file, "w") as f:
                json.dump(data, f, indent=2) # 'indent=2' makes the JSON file human-readable
                
        except (IOError, json.JSONDecodeError) as e:
            # Log any file access errors to the main rotation.log for debugging.
            logging.error(f"Error writing to honeypot log file: {e}")

# --- Generic Decoy Server Logic ---
def _start_decoy_server(port: int, service_type: str, banner: bytes):
    """
    A generic function to start a decoy TCP server. It listens on a given port,
    and for every connection, it logs the event and sends a fake banner.
    """
    
    # This inner function handles a single connection from an attacker.
    def connection_handler(conn, addr):
        try:
            # The 'addr' tuple contains the attacker's (IP, port).
            client_ip, client_port = addr
            
            # Log the event as soon as the connection is made.
            log_event(service_type, client_ip, client_port, port)
            
            # Send the fake banner to the attacker to deceive their scanning tools.
            conn.sendall(banner)
            
        except socket.error as e:
            # Log any network errors, but don't crash the server.
            logging.debug(f"Socket error on {service_type} honeypot: {e}")
        finally:
            # It's crucial to always close the connection to free up resources.
            conn.close()

    # This inner function is the main server loop that listens for new connections.
    def server_loop():
        try:
            # Create a new TCP socket.
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # This option allows the server to restart quickly without waiting
                # for the OS to release the port, which is useful for development.
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                
                # Bind the socket to all available network interfaces on the specified port.
                s.bind(("0.0.0.0", port))
                
                # Start listening for incoming connections.
                s.listen(5)
                logging.info(f"[{service_type}] Honeypot now listening on port {port}")
                
                # This loop runs forever, accepting new connections.
                while True:
                    conn, addr = s.accept()
                    # For each new connection, we spawn a new "daemon" thread to handle it.
                    # This is essential for handling multiple simultaneous connections
                    # without blocking the main server loop.
                    threading.Thread(target=connection_handler, args=(conn, addr), daemon=True).start()
        except OSError as e:
            # This error happens if the port is already in use.
            logging.error(f"Failed to bind {service_type} honeypot to port {port}: {e}")

    # Start the server_loop in a background thread. This is the key to making
    # the honeypot system non-blocking, allowing the main application to continue.
    threading.Thread(target=server_loop, daemon=True).start()

# --- Public Entrypoint Function ---
def launch_honeypots(config: dict):
    """
    Launches fake HTTP and SSH servers on random decoy ports, as defined in the config.
    This function is non-blocking and returns immediately.
    """
    honeypot_config = config.get("honeypot", {})
    http_range = honeypot_config.get("http_range", [8000, 9000])
    ssh_range = honeypot_config.get("ssh_range", [2000, 3000])

    # Get random, available ports for the decoys.
    http_port = random.randint(*http_range)
    ssh_port = random.randint(*ssh_range)

    # Define the fake banners. These are designed to look like common,
    # slightly outdated server versions, which are attractive targets for attackers.
    http_banner = b"HTTP/1.1 200 OK\r\nServer: Apache/2.4.41 (Ubuntu)\r\nContent-Type: text/html\r\n\r\n<h1>Welcome</h1>"
    ssh_banner = b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.1\r\n"

    # Launch the two decoy servers. Each will run in its own background thread.
    _start_decoy_server(http_port, "HTTP", http_banner)
    _start_decoy_server(ssh_port, "SSH", ssh_banner)
    
    logging.info("Honeypot services launched in background.")