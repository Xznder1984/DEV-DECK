"""
Sample plugin for DevDeck.
Demonstrates how to create plugins for extending DevDeck functionality.
"""

import typer
from typing import Dict, Callable


class SamplePlugin:
    """A sample plugin that adds a greeting command."""
    
    def __init__(self):
        self.name = "sample"
        self.version = "1.0.0"
    
    def register_commands(self) -> Dict[str, Callable]:
        """Register plugin commands.
        
        Returns:
            Dictionary mapping command names to functions
        """
        return {
            "greet": self.greet_command
        }
    
    def greet_command(self, name: str = typer.Argument("Developer", help="Name to greet")):
        """Greet a developer."""
        typer.echo(f"Hello, {name}! Welcome to DevDeck!")
    
    def on_load(self):
        """Called when the plugin is loaded."""
        print(f"Sample plugin v{self.version} loaded successfully!")


# Plugin metadata
plugin = SamplePlugin()

# This is how the plugin system would discover and load plugins
def load_plugin():
    """Load the sample plugin."""
    plugin.on_load()
    return plugin.register_commands()
