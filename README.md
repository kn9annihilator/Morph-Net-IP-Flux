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

+------------------------+
| Scheduler Engine |
+------------------------+
|
+------------------+
| IP Manager |
+------------------+
| |
Flush IP Assign IP
| |
+--------+ +--------+
|System | |Network |
+--------+ +--------+

+----------------------------+
| DNS Controller (Cloudflare)|
+----------------------------+

+---------------------+
| TLS Cert Generator |
+---------------------+

+------------------------+
| Honeypot Deployer |
+------------------------+

+------------------------+
| Red Team Simulators |
+------------------------+


---

## Installation

### Prerequisites

- Python 3.7+
- Linux/WSL (IP tools must be available)
- Git, Bash
- `iproute2`, `openssl`, `curl` for shell functionality
- Virtual environment recommended

### Setup

```bash
git clone https://github.com/yourusername/MorphNetIPFlux.git
cd MorphNetIPFlux
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt


Usage
python main.py
IP rotation begins.

DNS record is updated.

Honeypots are deployed.

Logs are stored in logs/.