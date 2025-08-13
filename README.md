# Morph Net IP Flux
> *You can't hit a target you can't see.*

![Stars](https://img.shields.io/github/stars/kn9annihilator/Morph-Net-IP-Flux?style=social)
![Last Commit](https://img.shields.io/github/last-commit/kn9annihilator/Morph-Net-IP-Flux?color=brightgreen)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20WSL-blue)
![Framework](https://img.shields.io/badge/framework-Python%20%7C%20Bash-yellow)
![Funny Badge](https://img.shields.io/badge/💀-Stay%20Invisible!-black)
![License](https://img.shields.io/badge/license-MIT-red)

---

## 📜 Table of Contents
- [Overview](#overview)
- [What's the Problem? The "Sitting Duck" Server](#whats-the-problem-the-sitting-duck-server)
- [Our Solution: The "Ghost" Server](#our-solution-the-ghost-server)
- [How It Works: The Core Features](#how-it-works-the-core-features)
- [Architecture: The Blueprint](#architecture-the-blueprint)
- [Real-World Deployment: The Stable Gateway](#project-deployment-the-stable-gateway)
- [Installation & Setup](#installation--setup)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Setup](#step-by-step-setup)
- [Running the Project](#running-the-project)
- [Usage Scenarios](#usage-scenarios)
- [Project Status](#project-status)
- [Testing](#testing)
- [Contributing](#contributing)
- [📝 License](#license)
- [Authors](#authors)


---

## Overview

**Morph Net IP Flux** is a Python and Bash-powered **Moving Target Defense (MTD)** framework designed to break the attacker's reconnaissance phase by continuously rotating IP addresses, TLS certificates, and DNS mappings. It transforms a web server into a moving, morphing ghost on the network.

---

## What's the Problem? The "Sitting Duck" Server

Imagine a fortress with a known location. Anyone can study it, map it, and plan a perfect breach. That's how traditional servers work—with static IPs attackers can probe for weeks.

This early phase of cyber-attacks, called **reconnaissance**, is the most exploited. If attackers can’t recon, they can’t attack.

---

## Our Solution: The "Ghost" Server

Instead of building taller walls, **we make the server vanish**. Morph Net IP Flux constantly changes:

- **Its Address** → via IP Rotation
- **Its Name** → via DNS API sync
- **Its Face** → via randomized TLS certificates

Every time the attacker thinks they found you, you're already gone. Their intel is outdated by design.

---

## How It Works: The Core Features

| Feature                     | Description |
|-----------------------------|-------------|
| **Dynamic IP Rotation**     | Randomly assigns new IPs from a pool at jittered intervals |
| **TLS Certificate Morphing**| Prevents JA3/JA3S fingerprinting with randomized certs |
| **DNS Sync (Cloudflare)**   | Updates domain records instantly via API |
| **Jitter-based Scheduler**  | Prevents timing predictability |
| **Decoy Deployment**        | Honeypots confuse attackers & fake open ports |
| **Multi-Log System**        | Tracks rotations, honeypot hits, and recon attempts |

---

## Architecture: The Blueprint

```js
│
├── core/          # Brain: IP, DNS, Scheduler, TLS, Honeypots
│   ├── ip_manager.py
│   ├── scheduler.py
│   ├── dns_controller.py
│   ├── tls_manager.py
│   ├── honeypot_deployer.py
│
│── setup.py # CLI dashboard for Linux Terminal
├── config/        # Configs: Secrets, Intervals, Pools
│   ├── default_config.yaml
│   ├── cloud_config.yaml
│   └── secrets.env
│
├── shell/         # OS-level scripts: IP assign, flush, TLS gen
│   ├── assign_ip.sh
│   ├── flush_ip.sh
│   ├── rotate_tls.sh
│
├── deploy/        # Docker/K8s/Cloud deploy scripts
│
├── integrations/  # Cloudflare, Proxies, Log APIs
│
├── redteam_sim/   # Red team recon emulators (nmap, etc.)
│
├── logs/          # All runtime logs
│
├── tests/         # Unit & functional tests
│
├── main.py        # Launches the entire system
├── requirements.txt

```
## Project Deployment: The Stable Gateway
"Won’t rotating IPs break user access?"

No. You deploy a Transparent Reverse Proxy as a fixed frontend. This stable proxy forwards requests to the MTD-powered server which lives on a rotating private network. Seamless to users. Hellish for hackers.

## Installation & Setup
### Prerequisites

| Tool                     | Why it's needed |
|-----------------------------|-------------|
| **Python 3.7+**     | Core Language |
| **Git**| Clone the Repository |
| **Bash Shell**   | To execute shell scripts (WSL/Git Bash/Linux) |
| **iproute2, curl**  | For IP handling and HTTP calls |
| **OpenSSL**        | Generate and rotate certificates |

### Step-by-Step Setup
1. Clone the Repository
```git
git clone https://github.com/kn9annihilator/Morph-Net-IP-Flux
cd Morph-Net-IP-Flux
```
2. Create & Activate Virtual Environment
```git
python -m venv .venv
source .venv/bin/activate  
```
For Windows:
```git
.venv\Scripts\activate
```
3. Install Dependencies
```bash
pip install -r requirements.txt
```
or
```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
```
4. Configure the Engine
```bash
config/default_config.yaml: Set IP pool, timing, etc.

secrets.env: Store API keys securely (copy from .env.example)
```
5. Run the Project!
```git
.venv/bin/python main.py  
```
Or just
```git
python main.py # if environment is activated
```

## Running the Project
You should see live logs like:
```js
2025-08-04 03:45:30,179 [INFO] - --- Morph Net IP Flux Engine Starting ---
2025-08-04 03:45:30,184 [WARNING] - API_TOKEN not found or not set in secrets.env. DNS updates will fail.
2025-08-04 03:45:30,184 [INFO] - Configuration loaded successfully.
2025-08-04 03:45:30,184 [INFO] - Deploying honeypot services...
2025-08-04 03:45:30,185 [INFO] - Honeypot services launched in background.
2025-08-04 03:45:30,185 [INFO] - [HTTP] Honeypot now listening on port 8343
2025-08-04 03:45:30,185 [INFO] - [SSH] Honeypot now listening on port 2041
2025-08-04 03:45:30,185 [INFO] - Starting the main MTD scheduler...
2025-08-04 03:45:30,186 [INFO] - Initializing scheduler thread...
2025-08-04 03:45:40,457 [INFO] - --- Morph Net IP Flux Engine Shutting Down ---
```
## Usage Scenarios
* Teaching advanced Red vs Blue tactics

* Simulating evasive C2 channels

* Research on Moving Target Defense (MTD)

* Obfuscating APIs or sensitive endpoints

* Securing cloud servers from persistent recon

# Project Status
Currently a stable prototype.

* Core MTD engine: working locally

* Functional IP + DNS + TLS rotation

* Production cloud deployment support (under test)

* Simulation mode enabled for safe testing

## Testing
Run Python unit tests:
```js
pytest tests/
```
Test Red Team emulation:
```js
bash redteam_sim/nmap_scan.sh
```

## Contributing
This project is open to improvement. Feel free to fork, contribute, and raise issues. Academic usage is encouraged with attribution.
## License

## Authors
Krishna Narula\\
Cybersecurity Researcher | MTD Enthusiast | Web App Tester\\

Tushar Sharma\\
AI ML Researcher | MTD Developer and Researcher

[![Connect with Krishna](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin&style=flat-square)](https://www.linkedin.com/in/krishnanarula/)\\
[![Connect with Tushar](https://img.shields.io/badge/LinkedIn-Connect-blue?logo=linkedin&style=flat-square)](https://www.linkedin.com/in/tusharssharma/)
