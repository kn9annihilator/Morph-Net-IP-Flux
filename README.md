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

 | Tool              | Version/Details                                             |
|--------------------|-------------------------------------------------------------|
| core/	             | Core logic modules for IP rotation, DNS, scheduler, etc.    |
| config/	         | Configuration files and environment variables.              |
| shell/             | Bash scripts for IP operations and TLS rotation.            |
| deploy/            | Deployment scripts for Docker, Kubernetes, and cloud init.  |
| integrations/	     | API integrations for DNS, proxies, and logging systems.     |
| redteam_sim/	     | Red-team simulation tools for scanning and recon.           |
| logs/	             | Stores runtime logs for IP changes, honeypot hits, etc.     |
| tests/	         | Unit and functional test scripts.                           |
| main.py	         | Entry point for launching the full system                   |
| setup.py	         | Python setup script for packaging.                          |
| .gitignore	     | Standard Git ignore rules.                                  |


---


## ⚙️ Installation & Setup
 This section guides you through setting up Morph Net IP Flux on a compatible system.

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

``` bash
git clone https://github.com/your-username/MorphNetIPFlux.git
cd MorphNetIPFlux
```

#### 2. Create a Virtual Environment
Linux / WSL:

``` bash	
python3 -m venv .venv
source .venv/bin/activate
```

Windows CMD:
``` bash
python -m venv .venv
.venv\Scripts\activate
```

#### 3. Install Dependencies
``` bash
pip install -r requirements.txt
```


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

``` bash
pytest tests/
```
You may also test shell integrations separately:

``` bash
redteam_sim/nmap_scan.sh
```

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