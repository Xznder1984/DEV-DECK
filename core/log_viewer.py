"""
Live log viewer for DevDeck.
Provides real-time log tailing with highlighting and filtering capabilities.
"""

import os
import time
import threading
from typing import List, Callable, Optional, Pattern
from pathlib import Path
import re
import logging


class LogViewer:
    """Views and monitors log files in real-time."""
    
    def __init__(self):
        self.callbacks: List[Callable[[str, str], None]] = []  # (line, level)
        self.watched_files: List[str] = []
        self.file_positions: dict = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)
    
    def add_callback(self, callback: Callable[[str, str], None]) -> None:
        """Add a callback for new log lines.
        
        Args:
            callback: Function to call with (line, level)
        """
        self.callbacks.append(callback)
    
    def watch_file(self, file_path: str) -> bool:
        """Start watching a log file.
        
        Args:
            file_path: Path to the log file
            
        Returns:
            True if watching started successfully, False otherwise
        """
        if not os.path.exists(file_path):
            self.logger.error(f"Log file does not exist: {file_path}")
            return False
        
        if file_path in self.watched_files:
            self.logger.warning(f"Already watching log file: {file_path}")
            return True
        
        self.watched_files.append(file_path)
        self.file_positions[file_path] = 0
        self.logger.info(f"Started watching log file: {file_path}")
        return True
    
    def unwatch_file(self, file_path: str) -> bool:
        """Stop watching a log file.
        
        Args:
            file_path: Path to the log file
            
        Returns:
            True if watching stopped successfully, False otherwise
        """
        if file_path not in self.watched_files:
            self.logger.warning(f"Not watching log file: {file_path}")
            return False
        
        self.watched_files.remove(file_path)
        if file_path in self.file_positions:
            del self.file_positions[file_path]
        self.logger.info(f"Stopped watching log file: {file_path}")
        return True
    
    def detect_log_level(self, line: str) -> str:
        """Detect the log level of a line.
        
        Args:
            line: Log line to analyze
            
        Returns:
            Log level ("ERROR", "WARNING", "INFO", "DEBUG", or "OTHER")
        """
        line_upper = line.upper()
        if "ERROR" in line_upper or "ERR" in line_upper:
            return "ERROR"
        elif "WARN" in line_upper or "WARNING" in line_upper:
            return "WARNING"
        elif "INFO" in line_upper:
            return "INFO"
        elif "DEBUG" in line_upper:
            return "DEBUG"
        else:
            return "OTHER"
    
    def _tail_files(self) -> None:
        """Internal method to tail log files."""
        while self.running:
            for file_path in self.watched_files:
                try:
                    # Check if file exists
                    if not os.path.exists(file_path):
                        continue
                    
                    # Get file size
                    file_size = os.path.getsize(file_path)
                    
                    # If file was truncated, reset position
                    if file_size < self.file_positions.get(file_path, 0):
                        self.file_positions[file_path] = 0
                    
                    # Read new content
                    with open(file_path, 'r') as f:
                        # Seek to last position
                        f.seek(self.file_positions.get(file_path, 0))
                        
                        # Read new lines
                        while True:
                            line = f.readline()
                            if not line:
                                break
                            
                            # Detect log level and call callbacks
                            level = self.detect_log_level(line)
                            for callback in self.callbacks:
                                try:
                                    callback(line.rstrip('\n'), level)
                                except Exception as e:
                                    self.logger.error(f"Error in log callback: {e}")
                        
                        # Update position
                        self.file_positions[file_path] = f.tell()
                
                except Exception as e:
                    self.logger.error(f"Error reading log file {file_path}: {e}")
            
            time.sleep(0.1)  # Check for new content every 100ms
    
    def start(self) -> None:
        """Start the log viewer."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._tail_files, daemon=True)
            self.thread.start()
            self.logger.info("Log viewer started")
    
    def stop(self) -> None:
        """Stop the log viewer."""
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("Log viewer stopped")


# Global log viewer instance
log_viewer = LogViewer()
