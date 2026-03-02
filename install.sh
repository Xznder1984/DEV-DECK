#!/bin/bash

# DevDeck Linux Installer
# This script installs DevDeck on Linux systems

set -e

echo "🚀 Installing DevDeck..."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root. Please run without sudo.${NC}"
   exit 1
fi

# Check dependencies
echo -e "${YELLOW}Checking dependencies...${NC}"

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3 and try again.${NC}"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}pip3 is not installed. Please install pip3 and try again.${NC}"
    exit 1
fi

# Create temp directory
TEMP_DIR=$(mktemp -d)
echo -e "${YELLOW}Created temporary directory: $TEMP_DIR${NC}"

# Cleanup function
cleanup() {
    echo -e "${YELLOW}Cleaning up...${NC}"
    rm -rf "$TEMP_DIR"
}

trap cleanup EXIT

# Clone the repository
echo -e "${YELLOW}Cloning DevDeck repository...${NC}"
git clone https://github.com/Xznder1984/DEV-DECK.git "$TEMP_DIR/devdeck" || {
    echo -e "${RED}Failed to clone repository. Trying with wget...${NC}"
    
    # Try downloading with wget if git fails
    wget -O "$TEMP_DIR/devdeck.zip" "https://github.com/Xznder1984/DEV-DECK/archive/main.zip" || {
        echo -e "${RED}Failed to download DevDeck. Please check your internet connection.${NC}"
        exit 1
    }
    
    # Extract the archive
    unzip "$TEMP_DIR/devdeck.zip" -d "$TEMP_DIR" || {
        echo -e "${RED}Failed to extract archive.${NC}"
        exit 1
    }
    
    # Move to correct directory
    mv "$TEMP_DIR/DEV-DECK-main" "$TEMP_DIR/devdeck"
}

# Navigate to the DevDeck directory
cd "$TEMP_DIR/devdeck"

# Install DevDeck
echo -e "${YELLOW}Installing DevDeck...${NC}"
pip3 install --user .

# Find the user's bin directory
USER_BIN_DIR="$HOME/.local/bin"

# Check if the bin directory exists
if [ ! -d "$USER_BIN_DIR" ]; then
    echo -e "${YELLOW}Creating $USER_BIN_DIR directory...${NC}"
    mkdir -p "$USER_BIN_DIR"
fi

# Copy the executable script
echo -e "${YELLOW}Creating executable script...${NC}"
cat > "$USER_BIN_DIR/devdeck" << 'EOF'
#!/bin/bash
# DevDeck launcher script

# Find the installed package location
PYTHON_USER_BASE=$(python3 -m site --user-base 2>/dev/null)
if [ $? -ne 0 ]; then
    PYTHON_USER_BASE="$HOME/.local"
fi

# Try to run the installed package first
if python3 -c "import devdeck" &> /dev/null; then
    python3 -m main "$@"
else
    # Fallback to local installation
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    PROJECT_DIR="$(dirname "$SCRIPT_DIR")/lib/python*/site-packages/devdeck-*"
    
    if [ -f "$PROJECT_DIR/main.py" ]; then
        python3 "$PROJECT_DIR/main.py" "$@"
    else
        echo "Error: DevDeck not found. Please reinstall."
        exit 1
    fi
fi
EOF

chmod +x "$USER_BIN_DIR/devdeck"

# Add to PATH if not already there
if [[ ":$PATH:" != *":$USER_BIN_DIR:"* ]]; then
    echo -e "${YELLOW}Adding $USER_BIN_DIR to PATH...${NC}"
    
    # Try to detect shell
    if [ -f "$HOME/.bashrc" ]; then
        SHELL_CONFIG="$HOME/.bashrc"
    elif [ -f "$HOME/.zshrc" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    else
        SHELL_CONFIG="$HOME/.profile"
    fi
    
    # Add to PATH if not already present
    if ! grep -q "export PATH=.*$USER_BIN_DIR" "$SHELL_CONFIG" 2>/dev/null; then
        echo "export PATH=\"\$PATH:$USER_BIN_DIR\"" >> "$SHELL_CONFIG"
        echo -e "${YELLOW}Added $USER_BIN_DIR to PATH in $SHELL_CONFIG${NC}"
        echo -e "${YELLOW}Please restart your terminal or run: source $SHELL_CONFIG${NC}"
    fi
fi

echo -e "${GREEN}✅ DevDeck installed successfully!${NC}"
echo -e "${GREEN}Run 'devdeck --help' to get started.${NC}"
echo -e "${YELLOW}Note: If the 'devdeck' command is not found, please restart your terminal or run: source $SHELL_CONFIG${NC}"
