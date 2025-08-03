# core/port_randomizer.py

import random
import yaml
import logging
import os
import socket

# Define the path for the output file where the randomized ports will be stored.
# This file serves as a record of the ports chosen for a particular session
# and can be used by other services for synchronization if needed.
PORT_MAP_FILE = os.path.join("config", "port_mapping.yaml")

def _is_port_available(port: int) -> bool:
    """
    Checks if a given TCP port is available to be used.

    This is an optimization to prevent the honeypot from failing to start
    if the randomly selected port is already in use by another application.

    Returns:
        bool: True if the port is available, False otherwise.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # The SO_REUSEADDR flag is set to allow immediate reuse of the port,
            # which is good practice for server applications.
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Try to bind to the port. If this succeeds, the port is free.
            s.bind(("0.0.0.0", port))
            return True
        except OSError:
            # If an OSError occurs, it means the port is already in use.
            return False

def _get_random_available_port(start: int, end: int, max_retries: int = 10) -> int | None:
    """
    Finds a random, available port within a given range.

    It will try a limited number of times to find a free port to avoid
    getting stuck in an infinite loop on a very busy system.

    Args:
        start (int): The beginning of the port range.
        end (int): The end of the port range.
        max_retries (int): The maximum number of attempts to find a free port.

    Returns:
        int | None: An available port number, or None if no port could be found.
    """
    for _ in range(max_retries):
        port = random.randint(start, end)
        if _is_port_available(port):
            return port
    logging.warning(f"Could not find an available port in range [{start}-{end}] after {max_retries} retries.")
    return None

def generate_and_save_ports(config: dict) -> dict:
    """
    Generates random, available ports for decoy services based on ranges
    defined in the config file and saves them to a separate YAML file.

    Args:
        config (dict): The global configuration dictionary.

    Returns:
        dict: A dictionary containing the newly randomized port mappings.
    """
    # Load the port ranges from the 'honeypot' section of the config.
    honeypot_config = config.get("honeypot", {})
    port_ranges = {
        "http": honeypot_config.get("http_range", [8000, 9000]),
        "ssh": honeypot_config.get("ssh_range", [2000, 3000])
    }

    # Create a new dictionary to hold the randomized port for each service.
    randomized_ports = {}
    for service, (start, end) in port_ranges.items():
        port = _get_random_available_port(start, end)
        if port:
            randomized_ports[service] = port
        else:
            # If no port could be found, we log an error and skip this service.
            logging.error(f"Failed to allocate a random port for the '{service}' decoy service.")

    # Save the resulting map to the port_mapping.yaml file if any ports were found.
    if randomized_ports:
        try:
            os.makedirs("config", exist_ok=True)
            with open(PORT_MAP_FILE, 'w') as f:
                yaml.dump(randomized_ports, f, default_flow_style=False)
            logging.info(f"Saved randomized port map: {randomized_ports}")
        except IOError as e:
            logging.error(f"Failed to save port map to {PORT_MAP_FILE}: {e}")

    return randomized_ports

# Note: This module is currently a utility that can be called if needed.
# The `honeypot_deployer` directly handles its own port randomization internally.
# This script is maintained for future use cases, such as needing a centralized
# port map for other services like a firewall or an IDS.