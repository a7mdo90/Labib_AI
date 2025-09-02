#!/bin/bash

# Labib Telegram Bot Service Installation Script
# This script installs the bot as a systemd service for automatic startup

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}=== $1 ===${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

print_header "Installing Labib Telegram Bot as System Service"

# Set installation directory
INSTALL_DIR="/opt/labib-bot"
SERVICE_FILE="labib-bot.service"

print_status "Installing bot to $INSTALL_DIR..."

# Create installation directory
mkdir -p "$INSTALL_DIR"

# Copy all bot files to installation directory
print_status "Copying bot files..."
cp -r . "$INSTALL_DIR/"

# Make scripts executable
print_status "Making scripts executable..."
chmod +x "$INSTALL_DIR"/*.sh
chmod +x "$INSTALL_DIR"/manage_bot.sh
chmod +x "$INSTALL_DIR"/deploy_droplet.sh

# Copy service file to systemd directory
print_status "Installing systemd service..."
cp "$SERVICE_FILE" /etc/systemd/system/

# Reload systemd daemon
print_status "Reloading systemd daemon..."
systemctl daemon-reload

# Enable the service for automatic startup
print_status "Enabling service for automatic startup..."
systemctl enable labib-bot.service

# Set proper permissions
print_status "Setting permissions..."
chown -R root:root "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
chmod 644 "$INSTALL_DIR"/*.py
chmod 644 "$INSTALL_DIR"/*.yml
chmod 644 "$INSTALL_DIR"/*.md
chmod 644 "$INSTALL_DIR"/*.txt
chmod 644 "$INSTALL_DIR"/*.json

# Create logs directory with proper permissions
mkdir -p "$INSTALL_DIR/logs"
chmod 755 "$INSTALL_DIR/logs"

print_status "✅ Service installed successfully!"

echo ""
print_header "Service Management Commands"
echo "Start service:    sudo systemctl start labib-bot"
echo "Stop service:     sudo systemctl stop labib-bot"
echo "Restart service:  sudo systemctl restart labib-bot"
echo "Check status:     sudo systemctl status labib-bot"
echo "View logs:        sudo journalctl -u labib-bot -f"
echo "Disable service:  sudo systemctl disable labib-bot"

echo ""
print_header "Next Steps"
echo "1. Start the service: sudo systemctl start labib-bot"
echo "2. Check status: sudo systemctl status labib-bot"
echo "3. The bot will now start automatically on server reboot"

echo ""
print_warning "Important Notes:"
echo "- The bot is now installed in $INSTALL_DIR"
echo "- All future updates should be done in $INSTALL_DIR"
echo "- The service will start automatically on server boot"
echo "- Use systemctl commands to manage the service"

print_status "Installation completed! 🚀"
