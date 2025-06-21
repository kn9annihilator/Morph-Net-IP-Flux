"# Morph Net IP Flux" 
"WIP: README reset after conflict" 


We’ve outlined detailed attack vectors and how this project defends against them in our [Threat Model](Impt_Docs/threat_model.md).

- IP address rotation using randomized intervals
- Shell-level control over assignment and flushing
- Configurable via YAML
- Integration-ready with DNS, proxies, and honeypots
- Logging and monitoring support
- Modular Python design for extensibility

---

##  Getting Started

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure `default_config.yaml` under `config/`
4. Make shell scripts executable:
   ```bash
   chmod +x shell/*.sh
   ```
5. Run the scheduler:
   ```bash
   python core/scheduler.py
   ```

---

## Example Config (config/default_config.yaml)
```yaml
ip_pool:
  - 192.168.1.100
  - 192.168.1.101
  - 192.168.1.102

network_interface: eth0

rotation_interval:
  min: 300
  max: 600
```

---

##  Future Modules
- DNS update automation
- TLS cert rotation
- Port obfuscation
- Decoy honeypots
- Red team attack simulation

---

## License
MIT License

---

##  Author
Maintained by [Krishna Narula](https://github.com/kn9annihilator)

---

## Project Status
Project is under active development.
Shell scripts and rotation scheduler functional.
