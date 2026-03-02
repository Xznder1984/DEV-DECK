"""
System monitoring utilities for DevDeck.
Provides real-time system metrics including CPU, RAM, disk, and network usage.
"""

import psutil
import time
from typing import Dict, Any, Tuple
import threading
from datetime import datetime


class SystemMonitor:
    """Monitors system resources and provides real-time metrics."""
    
    def __init__(self):
        self._last_net_io = psutil.net_io_counters()
        self._last_time = time.time()
    
    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        return psutil.cpu_percent(interval=1)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics."""
        memory = psutil.virtual_memory()
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent,
            "free": memory.free
        }
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get disk usage statistics."""
        disk = psutil.disk_usage('/')
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": (disk.used / disk.total) * 100 if disk.total > 0 else 0
        }
    
    def get_network_usage(self) -> Dict[str, Any]:
        """Get network usage statistics."""
        net_io = psutil.net_io_counters()
        current_time = time.time()
        
        # Calculate bytes per second
        time_diff = current_time - self._last_time
        if time_diff > 0:
            bytes_sent_per_sec = (net_io.bytes_sent - self._last_net_io.bytes_sent) / time_diff
            bytes_recv_per_sec = (net_io.bytes_recv - self._last_net_io.bytes_recv) / time_diff
        else:
            bytes_sent_per_sec = 0
            bytes_recv_per_sec = 0
        
        self._last_net_io = net_io
        self._last_time = current_time
        
        return {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "bytes_sent_per_sec": bytes_sent_per_sec,
            "bytes_recv_per_sec": bytes_recv_per_sec,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
    
    def get_uptime(self) -> str:
        """Get system uptime as a formatted string."""
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        return str(datetime.now() - datetime.fromtimestamp(boot_time))
    
    def get_all_stats(self) -> Dict[str, Any]:
        """Get all system statistics at once."""
        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "network": self.get_network_usage(),
            "uptime": self.get_uptime(),
            "timestamp": time.time()
        }


class ContinuousMonitor:
    """Continuously monitors system and calls callbacks with updated stats."""
    
    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.monitor = SystemMonitor()
        self.callbacks = []
        self.running = False
        self.thread = None
    
    def add_callback(self, callback) -> None:
        """Add a callback function to be called with stats updates."""
        self.callbacks.append(callback)
    
    def start(self) -> None:
        """Start continuous monitoring in a separate thread."""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.thread.start()
    
    def stop(self) -> None:
        """Stop continuous monitoring."""
        self.running = False
        if self.thread:
            self.thread.join()
    
    def _monitor_loop(self) -> None:
        """Main monitoring loop."""
        while self.running:
            stats = self.monitor.get_all_stats()
            for callback in self.callbacks:
                try:
                    callback(stats)
                except Exception as e:
                    print(f"Error in monitor callback: {e}")
            time.sleep(self.interval)


# Global monitor instances
system_monitor = SystemMonitor()
continuous_monitor = ContinuousMonitor()
