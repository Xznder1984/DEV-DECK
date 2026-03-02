"""
Folder watching utilities for DevDeck.
Monitors file system events and triggers configurable actions.
"""

import os
import subprocess
import threading
from typing import Dict, Callable, Optional, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import logging


class FileChangeHandler(FileSystemEventHandler):
    """Handles file system events and triggers actions."""
    
    def __init__(self, callback: Callable[[str, str], None]):
        """
        Initialize the handler.
        
        Args:
            callback: Function to call when file events occur (event_type, file_path)
        """
        self.callback = callback
        super().__init__()
    
    def on_created(self, event: FileSystemEvent) -> None:
        """Handle file creation events."""
        if not event.is_directory:
            self.callback("created", event.src_path)
    
    def on_deleted(self, event: FileSystemEvent) -> None:
        """Handle file deletion events."""
        if not event.is_directory:
            self.callback("deleted", event.src_path)
    
    def on_modified(self, event: FileSystemEvent) -> None:
        """Handle file modification events."""
        if not event.is_directory:
            self.callback("modified", event.src_path)
    
    def on_moved(self, event: FileSystemEvent) -> None:
        """Handle file move events."""
        if not event.is_directory:
            self.callback("moved", f"{event.src_path} -> {event.dest_path}")


class FolderWatcher:
    """Watches folders for file changes and executes commands."""
    
    def __init__(self):
        self.observer = Observer()
        self.watched_paths: Dict[str, str] = {}  # path -> command
        self.handlers: Dict[str, FileChangeHandler] = {}
        self.callbacks: List[Callable[[str, str, str], None]] = []  # (path, event_type, file_path)
        self.logger = logging.getLogger(__name__)
    
    def add_callback(self, callback: Callable[[str, str, str], None]) -> None:
        """Add a callback for file events.
        
        Args:
            callback: Function to call with (path, event_type, file_path)
        """
        self.callbacks.append(callback)
    
    def watch_folder(self, path: str, command: Optional[str] = None) -> bool:
        """Start watching a folder for changes.
        
        Args:
            path: Path to watch
            command: Command to execute on file changes (optional)
            
        Returns:
            True if watching started successfully, False otherwise
        """
        if not os.path.exists(path):
            self.logger.error(f"Path does not exist: {path}")
            return False
        
        if path in self.watched_paths:
            self.logger.warning(f"Already watching path: {path}")
            return True
        
        def handle_event(event_type: str, file_path: str) -> None:
            # Call registered callbacks
            for callback in self.callbacks:
                try:
                    callback(path, event_type, file_path)
                except Exception as e:
                    self.logger.error(f"Error in callback: {e}")
            
            # Execute command if provided
            if command:
                try:
                    self.logger.info(f"Executing command for {event_type} event: {command}")
                    result = subprocess.run(
                        command, 
                        shell=True, 
                        cwd=path, 
                        capture_output=True, 
                        text=True
                    )
                    if result.returncode != 0:
                        self.logger.warning(f"Command failed with exit code {result.returncode}: {result.stderr}")
                    else:
                        self.logger.info(f"Command output: {result.stdout}")
                except Exception as e:
                    self.logger.error(f"Failed to execute command '{command}': {e}")
        
        handler = FileChangeHandler(handle_event)
        self.observer.schedule(handler, path, recursive=True)
        self.watched_paths[path] = command
        self.handlers[path] = handler
        
        self.logger.info(f"Started watching folder: {path}")
        return True
    
    def unwatch_folder(self, path: str) -> bool:
        """Stop watching a folder.
        
        Args:
            path: Path to stop watching
            
        Returns:
            True if watching stopped successfully, False otherwise
        """
        if path not in self.watched_paths:
            self.logger.warning(f"Not watching path: {path}")
            return False
        
        # Note: Watchdog doesn't easily support unscheduling individual paths
        # We'll just remove from our tracking but keep observer running
        del self.watched_paths[path]
        del self.handlers[path]
        self.logger.info(f"Stopped watching folder: {path}")
        return True
    
    def start(self) -> None:
        """Start the folder watcher."""
        self.observer.start()
        self.logger.info("Folder watcher started")
    
    def stop(self) -> None:
        """Stop the folder watcher."""
        self.observer.stop()
        self.observer.join()
        self.logger.info("Folder watcher stopped")


# Global folder watcher instance
folder_watcher = FolderWatcher()
