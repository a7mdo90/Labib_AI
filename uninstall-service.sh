#!/bin/bash

# Labib Telegram Bot Service Uninstallation Script
# This script removes the bot systemd service

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

print_header "Uninstalling Labib Telegram Bot Service"

INSTALL_DIR="/opt/labib-bot"
SERVICE_NAME="labib-bot.service"

# Stop and disable the service
print_status "Stopping and disabling service..."
systemctl stop "$SERVICE_NAME" 2>/dev/null || true
systemctl disable "$SERVICE_NAME" 2>/dev/null || true

# Remove service file
print_status "Removing systemd service file..."
rm -f "/etc/systemd/system/$SERVICE_NAME"

# Reload systemd daemon
print_status "Reloading systemd daemon..."
systemctl daemon-reload

# Ask if user wants to remove installation directory
echo ""
print_warning "Do you want to remove the installation directory ($INSTALL_DIR)?"
print_warning "This will delete all bot files, logs, and data!"
echo ""
read -p "Type 'yes' to confirm removal: " confirm

if [ "$confirm" = "yes" ]; then
    print_status "Removing installation directory..."
    rm -rf "$INSTALL_DIR"
    print_status "✅ Installation directory removed"
else
    print_status "Installation directory kept at $INSTALL_DIR"
fi

print_status "✅ Service uninstalled successfully!"

echo ""
print_header "What was removed:"
echo "- Systemd service: $SERVICE_NAME"
echo "- Service file: /etc/systemd/system/$SERVICE_NAME"
if [ "$confirm" = "yes" ]; then
    echo "- Installation directory: $INSTALL_DIR"
else
    echo "- Installation directory: $INSTALL_DIR (kept)"
fi

echo ""
print_status "The bot service has been completely removed from the system."
