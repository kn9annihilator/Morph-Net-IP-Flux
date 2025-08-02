# main.py

import os
import time
import logging
import yaml
from dotenv import load_dotenv

# Import the functions from our refactored core modules
from core.scheduler import start_scheduler
from core.honeypot_deployer import launch_honeypots
# We will handle port_randomizer later; it's not critical for the core loop.

def initialize():
    """Loads configuration, sets up global logging, and creates directories."""
    # 1. Create necessary directories if they don't exist
    os.makedirs("logs", exist_ok=True)
    os.makedirs("certs", exist_ok=True)

    # 2. Setup global logging to print to console and file
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[
            logging.FileHandler("logs/rotation.log"),
            logging.StreamHandler() # This sends logs to the console
        ]
    )
    logging.info("--- Morph Net IP Flux Engine Starting ---")

    # 3. Load configurations from YAML and .env
    try:
        with open("config/default_config.yaml", "r") as f:
            config = yaml.safe_load(f)
        
        # Load secrets from .env file
        load_dotenv("secrets.env")
        api_token = os.getenv("API_TOKEN")
        
        if not api_token or api_token == "YOUR_CLOUDFLARE_API_TOKEN":
            logging.warning("API_TOKEN not found or not set in secrets.env. DNS updates will fail.")
        
        # Inject the secret into the config dictionary for easy passing
        if "dns" not in config: config["dns"] = {}
        config["dns"]["api_token"] = api_token
        
        logging.info("Configuration loaded successfully.")
        return config
    except FileNotFoundError:
        logging.critical("FATAL: config/default_config.yaml not found. Exiting.")
        exit(1)
    except Exception as e:
        logging.critical(f"FATAL: Error loading configuration: {e}. Exiting.")
        exit(1)

def main():
    """Main entry point for the application."""
    config = initialize()

    # Deploy Honeypots in the background
    logging.info("Deploying honeypot services...")
    launch_honeypots(config)

    # Start the main IP rotation scheduler in the background
    logging.info("Starting the main MTD scheduler...")
    start_scheduler(config)

    logging.info("--- All services initialized. Monitoring in progress... ---")

    # Keep the main thread alive to allow background threads to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("--- Morph Net IP Flux Engine Shutting Down ---")

if __name__ == "__main__":
    # Before running, ensure you have the necessary packages installed:
    # pip install python-dotenv PyYAML requests cryptography
    main()