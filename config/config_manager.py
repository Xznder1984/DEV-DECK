"""
Configuration manager for DevDeck application.
Handles loading, saving, and managing application settings.
"""

import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class ProjectConfig:
    """Represents a single project configuration."""
    
    def __init__(self, name: str, path: str, startup_cmd: str = "", test_cmd: str = "", watch_mode: bool = False):
        self.name = name
        self.path = path
        self.startup_cmd = startup_cmd
        self.test_cmd = test_cmd
        self.watch_mode = watch_mode
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert project config to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "startup_cmd": self.startup_cmd,
            "test_cmd": self.test_cmd,
            "watch_mode": self.watch_mode
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectConfig':
        """Create project config from dictionary."""
        return cls(
            name=data.get("name", ""),
            path=data.get("path", ""),
            startup_cmd=data.get("startup_cmd", ""),
            test_cmd=data.get("test_cmd", ""),
            watch_mode=data.get("watch_mode", False)
        )


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or os.path.expanduser("~/.devdeck/config.json")
        self.projects: List[ProjectConfig] = []
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    self.projects = [
                        ProjectConfig.from_dict(project_data) 
                        for project_data in data.get("projects", [])
                    ]
            else:
                # Create default config directory
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                self.save_config()
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            self.projects = []
    
    def save_config(self) -> None:
        """Save configuration to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            data = {
                "projects": [project.to_dict() for project in self.projects]
            }
            
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def add_project(self, project: ProjectConfig) -> None:
        """Add a new project to the configuration."""
        self.projects.append(project)
        self.save_config()
    
    def remove_project(self, project_name: str) -> bool:
        """Remove a project from the configuration by name."""
        initial_count = len(self.projects)
        self.projects = [p for p in self.projects if p.name != project_name]
        if len(self.projects) < initial_count:
            self.save_config()
            return True
        return False
    
    def get_project(self, project_name: str) -> Optional[ProjectConfig]:
        """Get a project by name."""
        for project in self.projects:
            if project.name == project_name:
                return project
        return None
    
    def update_project(self, project_name: str, updated_project: ProjectConfig) -> bool:
        """Update an existing project."""
        for i, project in enumerate(self.projects):
            if project.name == project_name:
                self.projects[i] = updated_project
                self.save_config()
                return True
        return False


# Global config manager instance
config_manager = ConfigManager()
