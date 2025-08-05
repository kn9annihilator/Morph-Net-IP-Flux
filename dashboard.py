#!/usr/bin/env python
# dashboard.py

import time
import json
import os
import re
from datetime import datetime, timezone

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn

# --- File Paths ---
STATUS_FILE = "logs/status.json"
ROTATION_LOG_FILE = "logs/rotation.log"
HONEYPOT_LOG_FILE = "logs/honeypot_hits.json"

console = Console()

def read_json_file(file_path: str, default_value=None):
    """Safely reads and parses a JSON file."""
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

def parse_log_file(file_path: str, num_lines: int = 200) -> list[Text]:
    """
    Reads and parses the last N lines of the log file, adding color.
    Increased to 200 lines to provide a larger, scrollable history.
    """
    if not os.path.exists(file_path):
        return [Text("Log file not found.", style="red")]
    
    parsed_lines = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-num_lines:]
            for line in lines:
                line = line.strip()
                if not line: continue
                
                if "[INFO]" in line: style = "green"
                elif "[WARNING]" in line: style = "yellow"
                elif "[ERROR]" in line or "[CRITICAL]" in line: style = "bold red"
                else: style = "white"
                
                line = re.sub(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} ', '', line)
                parsed_lines.append(Text(line, style=style))
        return parsed_lines
    except IOError:
        return [Text("Error reading log file.", style="red")]

def make_layout() -> Layout:
    """Defines the layout of the dashboard."""
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=11),
        Layout(ratio=1, name="main"),
        Layout(size=3, name="footer"),
    )
    layout["main"].split_row(Layout(name="side"), Layout(name="body", ratio=2))
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
    sub_header = Text("A Moving Target Defense Framework for Proactive Cyber Deception", style="bold white", justify="center")
    combined_text = Text("\n").join([header_text, credit_text, sub_header])
    return Panel(combined_text, border_style="blue")

def create_status_panel(status: dict, progress: Progress) -> Panel:
    """Creates the panel showing the current MTD engine status."""
    if not isinstance(status, dict):
        status = {"status": "Error", "current_ip": "Invalid status file"}

    # Use a simple table to structure the status info and the progress bar
    status_table = Table.grid(expand=True)
    status_table.add_row(Text(f"Status: ", style="bold"), Text(f"{status.get('status', 'N/A')}", style="green" if status.get('status') in ["Running", "Waiting"] else "yellow"))
    status_table.add_row(Text(f"Mode: ", style="bold"), Text(f"{status.get('mode', 'N/A').capitalize()}", style="cyan"))
    status_table.add_row(Text(f"Active IP: ", style="bold"), Text(f"{status.get('current_ip', 'N/A')}", style="magenta"))
    status_table.add_row(Text(f"Total Rotations: ", style="bold"), Text(f"{status.get('total_rotations', 0)}", style="white"))
    status_table.add_row(progress) # Add the progress bar as its own row

    return Panel(status_table, title="[bold blue]Engine Status[/]", border_style="blue")

def create_honeypot_panel() -> Panel:
    """Creates the panel showing the latest honeypot hits."""
    hits = read_json_file(HONEYPOT_LOG_FILE, default_value=[])
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
                table.add_row("Invalid Time", hit.get('service', '?'), hit.get('source_ip', '?'))
    return Panel(table, title="[bold red]Honeypot Activity[/]", border_style="red")

def run_dashboard():
    """Initializes and runs the live dashboard."""
    layout = make_layout()
    layout["header"].update(create_header())
    layout["footer"].update(Text("Press Ctrl+C to exit", style="dim", justify="center"))

    progress = Progress(
        TextColumn("[bold white]Next Rotation:[/bold white]"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    )
    rotation_task = progress.add_task("...", total=100)

    # Give the main engine a moment to start
    time.sleep(1)

    try:
        with Live(layout, screen=True, redirect_stderr=False, vertical_overflow="visible") as live:
            while True:
                status = read_json_file(STATUS_FILE, default_value={})
                
                next_rotation_str = status.get('next_rotation_in', '0s')
                try:
                    # Extract number from string like "280s"
                    total_seconds = int(re.sub(r'\D', '', next_rotation_str)) if next_rotation_str else 1
                    base_interval = int(re.sub(r'\D', '', status.get('base_interval', '300s'))) if status.get('base_interval') else 300
                    
                    if status.get('status') == "Waiting":
                        completed = base_interval - total_seconds
                        progress.update(rotation_task, total=base_interval, completed=completed)
                    else:
                        progress.update(rotation_task, total=100, completed=100, description="In Progress...")
                except (ValueError, TypeError):
                    progress.update(rotation_task, total=100, completed=0, description="N/A")

                # Update all panels
                rotation_log_content = Text("\n").join(parse_log_file(ROTATION_LOG_FILE))
                layout["body"].update(Panel(rotation_log_content, title="[bold green]Live MTD Log[/]", border_style="green"))
                layout["status"].update(create_status_panel(status, progress))
                layout["honeypot"].update(create_honeypot_panel())
                
                time.sleep(1)
    except KeyboardInterrupt:
        console.print("\nDashboard stopped.")
    except Exception as e:
        console.print(f"\n[bold red]Dashboard crashed with an error:[/bold red]")
        console.print(e)

if __name__ == "__main__":
    run_dashboard()
