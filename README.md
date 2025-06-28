# Morph Net IP Flux  
**Dynamic Moving Target Defense using Virtualized IP Rotation**

## Table of Contents
- [Overview](#overview)
- [Motivation](#motivation)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Technical Components](#technical-components)
- [Security & Threat Model](#security--threat-model)
- [Project Structure](#project-structure)
- [Testbed Setup](#testbed-setup)
- [Research & Industry Relevance](#research--industry-relevance)
- [License](#license)
- [Author](#author)

---

## Overview

**Morph Net IP Flux** is a Python and Shell-based cybersecurity framework that leverages **Moving Target Defense (MTD)** to safeguard web servers and cloud systems from enumeration, reconnaissance, and targeted attacks. It achieves this by dynamically rotating public-facing IP addresses, deploying honeypots, and spoofing attacker reconnaissance through behavioral obfuscation.

---

## Motivation

Traditional IP-based protections are static and predictable, making them vulnerable to:
- Automated scanning
- Reconnaissance by APTs
- IP-blacklisting circumvention
- Reverse engineering and targeting

This project was built to **break the attacker's kill chain at the earliest possible phase** — reconnaissance.

---

## Key Features

- **Dynamic IP Rotation**: Randomly replaces active IP addresses at configurable intervals.
- **Honeypot Deployment**: Launches lightweight HTTP and SSH decoy services to mislead attackers.
- **TLS Certificate Rotation**: Auto-generates and rotates TLS certificates to defeat JA3 fingerprinting.
- **Cloudflare DNS API Integration**: Seamless DNS record updates.
- **Jitter-based Scheduler**: Obfuscates timing patterns to resist statistical detection.
- **Multi-log System**: Logs every event (IP change, honeypot hit, attacker behavior, etc.)
- **Pluggable Modules**: Modular architecture to plug in future network defenses.

---

## Architecture

│
├── core/ # Core logic modules (IP, DNS, Scheduler)
│ ├── ip_manager.py
│ ├── scheduler.py
│ ├── port_manager.py
│ ├── dns_controller.py
│ ├── honeypot_deployer.py
│ └── tls_manager.py
│
├── config/ # Config files
│ ├── default_config.yaml
│ ├── cloud_config.yaml
│ └── secrets.env
│
├── shell/ # Shell scripts for IP management
│ ├── assign_ip.sh
│ ├── flush_ip.sh
│ ├── port_knock.sh
│ └── rotate_tls.sh
│
├── deploy/ # Docker/Kubernetes/Cloud deploy scripts
│ ├── Dockerfile
│ ├── docker-compose.yaml
│ ├── k8s.yaml
│ └── cloud_init.sh
│
├── integrations/ # Cloud/Proxy/API integrations
│ ├── cloudflare_api.py
│ ├── proxy_sync.py
│ └── ELK_logger.py
│
├── redteam_sim/ # Red team recon simulation tools
│ ├── scanner_emulator.py
│ ├── behavior_recon.py
│ └── nmap_scan.sh
│
├── docs/ # Documentation
│ ├── README.md
│ ├── threat_model.md
│ ├── architecture.md
│ └── research_refs.md
│
├── logs/ # Runtime logs
│ ├── rotation.log
│ ├── attack_trace.log
│ └── honeypot_hits.json
│
├── tests/ # Unit & functional tests
│ ├── test_ip_rotation.py
│ ├── test_dns_behavior.py
│ └── test_tls_rotation.py
│
├── main.py # Central entry point
├── requirements.txt # Python dependencies
├── setup.py # Packaging
└── .gitignore



## Installation and Setup

---

## ⚙️ Installation & Setup

### Prerequisites

| Tool               | Version/Details        |
|--------------------|------------------------|
| Python             | 3.7+                   |
| Git                | Latest                 |
| Bash Shell         | WSL / Git Bash / Linux |
| Tools              | iproute2, curl, openssl|
| OS                 | Linux / WSL2 (Windows) |

---

### Step-by-Step Guide

#### 1. Clone the Repository

`code`	
git clone https://github.com/your-username/MorphNetIPFlux.git
cd MorphNetIPFlux

#### 2. Create a Virtual Environment
Linux / WSL:

`code`	
python3 -m venv .venv
source .venv/bin/activate


Windows CMD:
`code`	
python -m venv .venv
.venv\Scripts\activate

#### 3. Install Dependencies
''' bash
pip install -r requirements.txt




### Prerequisites

- Python 3.7+
- Linux/WSL (IP tools must be available)
- Git, Bash
- `iproute2`, `openssl`, `curl` for shell functionality
- Virtual environment recommended

Running the Project
Run the full system using:

bash
python main.py
You will see output such as:

[+] Morph Net IP Flux — Dynamic Defense Engine Starting...
[+] Rotating IP from 192.168.1.100 to 192.168.1.101...
[✓] DNS record updated for example.com ➜ 192.168.1.101
[✓] Honeypots running on decoy ports.
[✓] Scheduler launched.
All activity will be logged in logs/rotation.log.

### Usage Scenarios
Simulating evasive Command & Control (C2) networks

Teaching real-world Red vs Blue strategies

Research on MTD (Moving Target Defense)

Obfuscating traffic to hide high-value APIs

Defending critical infrastructure from advanced recon

### Testing
Run unit tests:

`code`
pytest tests/
You may also test shell integrations separately:

`code`	
redteam_sim/nmap_scan.sh

### License
This project is licensed under the MIT License.
See [LICENSE](#license) for more details.

### References
NIST Special Publication 800-160: Developing Cyber Resilient Systems

JA3 TLS Fingerprinting: https://github.com/salesforce/ja3

DHS Moving Target Defense Research

Cloudflare API Docs

OWASP C2 Guidance

## Contributing
This is an evolving research project. Contributions, forks, and academic usage are welcome. Please raise issues or submit pull requests.

Author
Krishna Narula
[LinkedIn](#linkedin.com/krishnanarula)