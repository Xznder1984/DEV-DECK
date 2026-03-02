#!/usr/bin/env python3
"""
DevDeck - A powerful local developer control panel for programmers and IT enthusiasts.

This is the main entry point for the DevDeck application.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from cli.cli import app as cli_app
from web.server import run_web_server


def main():
    """Main entry point for DevDeck application."""
    if len(sys.argv) > 1 and sys.argv[1] in ["web", "server"]:
        # Run web server
        run_web_server()
    else:
        # Run CLI app
        cli_app()


if __name__ == "__main__":
    main()
