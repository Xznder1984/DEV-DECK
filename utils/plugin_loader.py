"""
Plugin loader for DevDeck.
Discovers and loads plugins from the plugins directory.
"""

import os
import importlib.util
from typing import Dict, Callable, List
from pathlib import Path


class PluginLoader:
    """Loads and manages DevDeck plugins."""
    
    def __init__(self, plugins_dir: str = "plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.loaded_plugins: Dict[str, Dict[str, Callable]] = {}
    
    def discover_plugins(self) -> List[str]:
        """Discover available plugins.
        
        Returns:
            List of plugin module names
        """
        plugins = []
        if self.plugins_dir.exists():
            for file in self.plugins_dir.iterdir():
                if file.suffix == ".py" and file.name != "__init__.py":
                    plugins.append(file.stem)
        return plugins
    
    def load_plugin(self, plugin_name: str):
        """Load a plugin by name."""
        plugin_file = self.plugins_dir / f"{plugin_name}.py"
        if not plugin_file.exists():
            raise FileNotFoundError(f"Plugin {plugin_name} not found")
        
        # Load the module
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # Check if the module has a load_plugin function
        if hasattr(module, "load_plugin"):
            commands = module.load_plugin()
            if isinstance(commands, dict):
                self.loaded_plugins[plugin_name] = commands
                print(f"Loaded plugin: {plugin_name}")
            else:
                print(f"Plugin {plugin_name} did not return valid commands")
        else:
            print(f"Plugin {plugin_name} does not have a load_plugin function")
    
    def load_all_plugins(self):
        """Load all discovered plugins."""
        plugin_names = self.discover_plugins()
        for plugin_name in plugin_names:
            try:
                self.load_plugin(plugin_name)
            except Exception as e:
                print(f"Failed to load plugin {plugin_name}: {e}")
    
    def get_all_commands(self) -> Dict[str, Callable]:
        """Get all commands from all loaded plugins.
        
        Returns:
            Dictionary mapping command names to functions
        """
        all_commands = {}
        for plugin_commands in self.loaded_plugins.values():
            all_commands.update(plugin_commands)
        return all_commands


# Global plugin loader instance
plugin_loader = PluginLoader()
