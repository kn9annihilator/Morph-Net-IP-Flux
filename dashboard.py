#!/usr/bin/env python
# dashboard.py

import time
import json
import os
from datetime import datetime, timezone

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# --- File Paths ---
STATUS_FILE = "logs/status.json"
ROTATION_LOG_FILE = "logs/rotation.log"
HONEYPOT_LOG_FILE = "logs/honeypot_hits.json"

console = Console()

def read_json_file(file_path: str, default_value=None):
    """
    Safely reads and parses a JSON file.

    Args:
        file_path (str): The path to the JSON file.
        default_value: The value to return if the file doesn't exist or is invalid.
    """
    if not os.path.exists(file_path):
        return default_value
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if not content:
                return default_value
            return json.loads(content)
    except (IOError, json.JSONDecodeError):
        return default_value

def read_log_file(file_path: str, num_lines: int = 30) -> str:
    """Reads the last N lines of a text file. Increased to 30 for more context."""
    if not os.path.exists(file_path):
        return "Log file not found."
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            return "".join(lines[-num_lines:])
    except IOError:
        return "Error reading log file."

def make_layout() -> Layout:
    """Defines the layout of the dashboard."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=11), # Increased size for the banner + credit
        Layout(ratio=1, name="main"),
        Layout(size=3, name="footer"),
    )

    layout["main"].split_row(
        Layout(name="side"),
        Layout(name="body", ratio=2),
    )
    
    layout["side"].split(Layout(name="status"), Layout(name="honeypot"))
    return layout

def create_header() -> Panel:
    """Creates the header panel with a stylized ASCII art title."""
    title_art = """
███╗   ███╗ ██████╗ ██████╗ ██████╗ ██╗  ██╗     ███╗   ███╗███████╗████████╗
████╗ ████║██╔═══██╗██╔══██╗██╔══██╗██║  ██║     ████╗  ███║██╔════╝╚══██╔══╝
██╔████╔██║██║   ██║██████╔╝██████╔╝███████║     ██╔██╗ ██║█████╗     ██║   
██║╚██╔╝██║██║   ██║██╔══██╗██╔═══╝ ██╔══██║     ██║╚██╗██║██╔══╝     ██║   
██║ ╚═╝ ██║╚██████╔╝██║  ██║██║     ██║  ██║     ██║ ╚████║███████╗   ██║   
╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝  ╚═╝     ╚═╝  ╚═══╝╚══════╝   ╚═╝   
    """
    
    header_text = Text(title_art, style="bold blue", justify="center")
    credit_text = Text("developed by kn9annihilator", style="dim white", justify="center")
    sub_header = Text(
        "A Moving Target Defense Framework for Proactive Cyber Deception",
        style="bold white",
        justify="center"
    )
    
    # Combine the art, credit, and subtitle
    combined_text = Text("\n").join([header_text, credit_text, sub_header])
    
    return Panel(combined_text, border_style="blue")


def create_status_panel() -> Panel:
    """Creates the panel showing the current MTD engine status."""
    status = read_json_file(STATUS_FILE, default_value={})
    
    # Add a runtime check to ensure status is a dictionary, making it robust.
    if not isinstance(status, dict):
        status = {"status": "Error", "current_ip": "Invalid status file"}

    status_text = Text()
    status_text.append("Status: ", style="bold")
    status_text.append(f"{status.get('status', 'N/A')}\n", style="green" if status.get('status') in ["Running", "Waiting"] else "yellow")
    status_text.append("Mode: ", style="bold")
    status_text.append(f"{status.get('mode', 'N/A').capitalize()}\n", style="cyan")
    status_text.append("Active IP: ", style="bold")
    status_text.append(f"{status.get('current_ip', 'N/A')}\n", style="magenta")
    status_text.append("Next Rotation: ", style="bold")
    status_text.append(f"{status.get('next_rotation_in', 'N/A')}\n", style="white")
    status_text.append("Total Rotations: ", style="bold")
    status_text.append(f"{status.get('total_rotations', 0)}\n", style="white")

    return Panel(status_text, title="[bold blue]Engine Status[/]", border_style="blue")

def create_honeypot_panel() -> Panel:
    """Creates the panel showing the latest honeypot hits."""
    hits = read_json_file(HONEYPOT_LOG_FILE, default_value=[])

    # Add a runtime check to ensure hits is a list.
    if not isinstance(hits, list):
        hits = []
    
    table = Table(title="Latest Hits", border_style="red")
    table.add_column("Timestamp", style="dim", no_wrap=True)
    table.add_column("Service", style="yellow")
    table.add_column("Source IP", style="red")

    for hit in reversed(hits[-5:]):
        ts_str = hit.get('timestamp', '').replace("Z", "+00:00")
        if ts_str and isinstance(hit, dict):
            try:
                ts = datetime.fromisoformat(ts_str).strftime('%H:%M:%S')
                table.add_row(ts, hit.get('service', '?'), hit.get('source_ip', '?'))
            except ValueError:
                # Handle cases where the timestamp might be malformed
                table.add_row("Invalid Time", hit.get('service', '?'), hit.get('source_ip', '?'))

    return Panel(table, title="[bold red]Honeypot Activity[/]", border_style="red")

def run_dashboard():
    """Initializes and runs the live dashboard."""
    layout = make_layout()

    layout["header"].update(create_header())
    layout["footer"].update(Text("Press Ctrl+C to exit", style="dim", justify="center"))
    layout["body"].update(Panel("Waiting for engine logs...", title="[bold green]Live MTD Log[/]", border_style="green"))
    layout["status"].update(create_status_panel())
    layout["honeypot"].update(create_honeypot_panel())

    # Give the main engine a moment to start and write the first status file
    time.sleep(1)

    with Live(layout, screen=True, redirect_stderr=False) as live:
        try:
            while True:
                time.sleep(1)
                # Update panels with the latest data
                rotation_log_content = read_log_file(ROTATION_LOG_FILE)
                layout["body"].update(Panel(Text(rotation_log_content), title="[bold green]Live MTD Log[/]", border_style="green"))
                layout["status"].update(create_status_panel())
                layout["honeypot"].update(create_honeypot_panel())
        except KeyboardInterrupt:
            pass
        except Exception as e:
            # This will catch any unexpected errors from the 'rich' library
            console.print(f"\n[bold red]Dashboard crashed with an error:[/bold red] {e}")


if __name__ == "__main__":
    run_dashboard()
