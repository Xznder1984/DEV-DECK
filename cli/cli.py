"""
Command-line interface for DevDeck.
Provides terminal-based access to all DevDeck features.
"""

import typer
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
import time

from config.config_manager import config_manager, ProjectConfig
from core.system_monitor import system_monitor

app = typer.Typer()
console = Console()


@app.command()
def monitor():
    """Display real-time system monitoring information."""
    console.print(Panel("DevDeck System Monitor", style="bold blue"))
    
    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=False,
        ) as progress:
            task = progress.add_task("Monitoring...", total=None)
            
            while True:
                stats = system_monitor.get_all_stats()
                
                table = Table(show_header=False, box=None)
                table.add_column("Metric", style="cyan", width=15)
                table.add_column("Value", style="green")
                
                table.add_row("CPU Usage", f"{stats['cpu']:.1f}%")
                table.add_row("Memory Used", f"{stats['memory']['used'] / (1024**3):.1f} GB")
                table.add_row("Memory %", f"{stats['memory']['percent']:.1f}%")
                table.add_row("Disk Used", f"{stats['disk']['used'] / (1024**3):.1f} GB")
                table.add_row("Disk %", f"{stats['disk']['percent']:.1f}%")
                table.add_row("Network Up", f"{stats['network']['bytes_sent_per_sec'] / 1024:.1f} KB/s")
                table.add_row("Network Down", f"{stats['network']['bytes_recv_per_sec'] / 1024:.1f} KB/s")
                table.add_row("Uptime", str(stats['uptime']).split('.')[0])
                
                console.clear()
                console.print(table)
                time.sleep(1)
                
    except KeyboardInterrupt:
        console.print("\n[yellow]Monitoring stopped.[/yellow]")


@app.command()
def watch(
    path: str = typer.Argument(..., help="Path to watch for file changes"),
    command: Optional[str] = typer.Option(None, "--command", "-c", help="Command to run on file changes")
):
    """Watch a directory for file changes and optionally run commands."""
    from core.folder_watcher import folder_watcher
    
    if not watch_path(path, command):
        raise typer.Exit(code=1)


def watch_path(path: str, command: Optional[str] = None) -> bool:
    """Helper function to watch a path."""
    try:
        from core.folder_watcher import folder_watcher
        
        # Set up file change callback
        def on_file_change(watch_path: str, event_type: str, file_path: str):
            console.print(f"[yellow]{event_type.upper()}[/yellow]: {file_path}")
            if command:
                console.print(f"[blue]EXECUTING[/blue]: {command}")
        
        folder_watcher.add_callback(on_file_change)
        
        # Start watching
        if folder_watcher.watch_folder(path, command):
            console.print(f"[green]Watching[/green] [bold]{path}[/bold]")
            if command:
                console.print(f"[blue]Command[/blue]: {command}")
            
            # Start the watcher
            folder_watcher.start()
            
            console.print("[yellow]Press Ctrl+C to stop watching...[/yellow]")
            try:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping watcher...[/yellow]")
                folder_watcher.stop()
                return True
        else:
            console.print("[red]Failed to start watching folder.[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Error watching folder:[/red] {e}")
        return False


@app.command()
def logs(
    file_path: str = typer.Argument(..., help="Path to log file to tail"),
    filter_error: bool = typer.Option(False, "--error", "-e", help="Filter only error messages"),
    filter_warning: bool = typer.Option(False, "--warning", "-w", help="Filter only warning messages")
):
    """Tail a log file with highlighting."""
    from core.log_viewer import log_viewer
    
    if not tail_logs(file_path, filter_error, filter_warning):
        raise typer.Exit(code=1)


def tail_logs(file_path: str, filter_error: bool = False, filter_warning: bool = False) -> bool:
    """Helper function to tail logs."""
    try:
        from core.log_viewer import log_viewer
        
        # Set up log callback
        def on_log_line(line: str, level: str):
            # Apply filters
            if filter_error and level != "ERROR":
                return
            if filter_warning and level != "WARNING":
                return
                
            # Apply coloring based on level
            if level == "ERROR":
                console.print(f"[red]ERROR[/red]: {line}")
            elif level == "WARNING":
                console.print(f"[yellow]WARN[/yellow]: {line}")
            elif level == "INFO":
                console.print(f"[green]INFO[/green]: {line}")
            else:
                console.print(f"[white]OTHER[/white]: {line}")
        
        log_viewer.add_callback(on_log_line)
        
        # Start watching the log file
        if log_viewer.watch_file(file_path):
            console.print(f"[green]Tailing log file:[/green] [bold]{file_path}[/bold]")
            
            # Start the viewer
            log_viewer.start()
            
            console.print("[yellow]Press Ctrl+C to stop tailing...[/yellow]")
            try:
                # Keep running until interrupted
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping log viewer...[/yellow]")
                log_viewer.stop()
                return True
        else:
            console.print("[red]Failed to start watching log file.[/red]")
            return False
            
    except Exception as e:
        console.print(f"[red]Error tailing logs:[/red] {e}")
        return False


@app.command()
def projects():
    """Manage projects in DevDeck."""
    show_projects()


def show_projects():
    """Display all configured projects."""
    projects = config_manager.projects
    
    if not projects:
        console.print("[yellow]No projects configured.[/yellow]")
        console.print("Add a project with: [bold]devdeck projects add[/bold]")
        return
    
    table = Table(title="DevDeck Projects")
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="magenta")
    table.add_column("Startup Cmd", style="green")
    table.add_column("Test Cmd", style="blue")
    table.add_column("Watch Mode", style="yellow")
    
    for project in projects:
        table.add_row(
            project.name,
            project.path,
            project.startup_cmd or "None",
            project.test_cmd or "None",
            "Enabled" if project.watch_mode else "Disabled"
        )
    
    console.print(table)


@app.command()
def add_project(
    name: str = typer.Option(..., "--name", "-n", help="Project name"),
    path: str = typer.Option(..., "--path", "-p", help="Project path"),
    startup_cmd: str = typer.Option("", "--startup", "-s", help="Startup command"),
    test_cmd: str = typer.Option("", "--test", "-t", help="Test command"),
    watch_mode: bool = typer.Option(False, "--watch", "-w", help="Enable watch mode")
):
    """Add a new project to DevDeck."""
    try:
        project = ProjectConfig(
            name=name,
            path=path,
            startup_cmd=startup_cmd,
            test_cmd=test_cmd,
            watch_mode=watch_mode
        )
        
        config_manager.add_project(project)
        console.print(f"[green]Project '[/green][bold]{name}[/bold][green]' added successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Error adding project:[/red] {e}")
        raise typer.Exit(code=1)


@app.command()
def remove_project(name: str = typer.Argument(..., help="Name of project to remove")):
    """Remove a project from DevDeck."""
    try:
        if config_manager.remove_project(name):
            console.print(f"[green]Project '[/green][bold]{name}[/bold][green]' removed successfully![/green]")
        else:
            console.print(f"[yellow]Project '[/yellow][bold]{name}[/bold][yellow]' not found.[/yellow]")
            
    except Exception as e:
        console.print(f"[red]Error removing project:[/red] {e}")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
