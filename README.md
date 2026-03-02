# DevDeck

A powerful local developer control panel for programmers and IT enthusiasts.

## Features

- **System Monitor**: Real-time CPU, RAM, disk, and network usage
- **Folder Watcher**: Monitor file changes and auto-run commands
- **Live Log Viewer**: Tail log files with error/warning highlighting
- **Project Manager**: Manage multiple projects with custom commands
- **Web Dashboard**: Modern web interface with live charts
- **CLI Interface**: Powerful command-line tools
- **Plugin System**: Extend functionality with custom plugins

## Installation

### Quick Installation

#### Linux/macOS (curl)
```bash
curl -fsSL https://raw.githubusercontent.com/Xznder1984/DEV-DECK/main/install.sh | bash
```

#### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/Xznder1984/DEV-DECK/main/install.ps1 | iex
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/Xznder1984/DEV-DECK.git
cd DEV-DECK

# Install dependencies
pip install -r requirements.txt

# Install as package (optional)
pip install .
```

## Usage

### CLI Mode

```bash
# System monitoring
devdeck monitor

# Folder watching
devdeck watch /path/to/project --command "pytest"

# Log viewing
devdeck logs /path/to/app.log

# Project management
devdeck projects
devdeck add-project --name "MyApp" --path "/path/to/app" --startup "npm run dev"
```

### Web Dashboard

```bash
# Start web server
devdeck web
```

Then visit http://localhost:8000

## Project Structure

```
devdeck/
├── core/          # Core functionality modules
├── cli/           # Command-line interface
├── web/           # Web dashboard
├── plugins/       # Plugin system
├── config/        # Configuration management
├── utils/         # Utility functions
├── main.py        # Main entry point
├── requirements.txt
└── README.md
```

## Requirements

- Python 3.7+
- See `requirements.txt` for Python package dependencies

## License

MIT
# DEV-DECK
