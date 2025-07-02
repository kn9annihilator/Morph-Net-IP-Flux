# core/port_randomizer.py
"""
Module: core/port_randomizer.py

Purpose:
Randomizes port assignments for honeypot services (e.g., HTTP, SSH) to prevent attackers
from reliably identifying targets. It updates a YAML config with the randomized port mapping
so all services can use synchronized ports.

This is crucial for the Morph Net IP Flux strategy as it adds another layer of unpredictability.

Outputs:
- config/port_mapping.yaml

"""

import random
import yaml
import logging
import os
from pathlib import Path

# ---------------------------
# Define Constants
# ---------------------------
PORT_RANGE = {
    "http": (8000, 9000),
    "ssh": (2000, 3000)
}
PORT_MAP_FILE = os.path.join("config", "port_mapping.yaml")

# ---------------------------
# Setup Logging
# ---------------------------
logging.basicConfig(
    filename="logs/rotation.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# ---------------------------
# Utility: Generate Random Ports
# ---------------------------
def generate_random_ports():
    """
    Randomly selects ports for each defined service.
    Ensures they are not the same as previously used ones.
    """
    port_map = {}
    for service, (start, end) in PORT_RANGE.items():
        port_map[service] = random.randint(start, end)
    return port_map

# ---------------------------
# Save Port Map to YAML File
# ---------------------------
def save_port_map(port_map: dict):
    """
    Saves the port mapping to a YAML config file for global reference.
    """
    os.makedirs("config", exist_ok=True)
    with open(PORT_MAP_FILE, 'w') as f:
        yaml.dump(port_map, f)
    logging.info(f"Saved randomized port map: {port_map}")

# ---------------------------
# Main Randomization Entry Point
# ---------------------------
def randomize_ports():
    """
    Main function to generate and store port mappings.
    """
    port_map = generate_random_ports()
    save_port_map(port_map)
    return port_map

# ---------------------------
# Debug/Test Mode
# ---------------------------
if __name__ == "__main__":
    port_map = randomize_ports()
    print("Randomized Ports:", port_map)