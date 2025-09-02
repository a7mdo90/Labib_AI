#!/bin/bash

# Labib Telegram Bot Service Manager
# Easy management of the systemd service

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

SERVICE_NAME="labib-bot.service"

# Function to show usage
show_usage() {
    echo "Labib Telegram Bot Service Manager"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the bot service"
    echo "  stop      - Stop the bot service"
    echo "  restart   - Restart the bot service"
    echo "  status    - Show service status"
    echo "  logs      - Show service logs"
    echo "  follow    - Follow service logs in real-time"
    echo "  enable    - Enable service for auto-start"
    echo "  disable   - Disable service auto-start"
    echo "  install   - Install the service"
    echo "  uninstall - Uninstall the service"
    echo "  help      - Show this help message"
    echo ""
    echo "Note: Some commands require sudo privileges"
}

# Function to check if service exists
service_exists() {
    systemctl list-unit-files | grep -q "$SERVICE_NAME"
}

# Function to start service
start_service() {
    print_header "Starting Labib Bot Service"
    
    if ! service_exists; then
        print_error "Service not installed. Run: sudo $0 install"
        exit 1
    fi
    
    print_status "Starting service..."
    sudo systemctl start "$SERVICE_NAME"
    
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "✅ Service started successfully!"
    else
        print_error "❌ Failed to start service!"
        sudo systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Function to stop service
stop_service() {
    print_header "Stopping Labib Bot Service"
    
    if ! service_exists; then
        print_error "Service not installed. Run: sudo $0 install"
        exit 1
    fi
    
    print_status "Stopping service..."
    sudo systemctl stop "$SERVICE_NAME"
    
    print_status "✅ Service stopped successfully!"
}

# Function to restart service
restart_service() {
    print_header "Restarting Labib Bot Service"
    
    if ! service_exists; then
        print_error "Service not installed. Run: sudo $0 install"
        exit 1
    fi
    
    print_status "Restarting service..."
    sudo systemctl restart "$SERVICE_NAME"
    
    sleep 3
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_status "✅ Service restarted successfully!"
    else
        print_error "❌ Failed to restart service!"
        sudo systemctl status "$SERVICE_NAME"
        exit 1
    fi
}

# Function to show status
show_status() {
    print_header "Service Status"
    
    if ! service_exists; then
        print_warning "Service not installed. Run: sudo $0 install"
        exit 1
    fi
    
    sudo systemctl status "$SERVICE_NAME" --no-pager
    
    echo ""
    print_status "Service Information:"
    echo "  Active: $(systemctl is-active $SERVICE_NAME)"
    echo "  Enabled: $(systemctl is-enabled $SERVICE_NAME)"
    echo "  Loaded: $(systemctl is-loaded $SERVICE_NAME)"
}

# Function to show logs
show_logs() {
    print_header "Service Logs (Last 50 lines)"
    
    if ! service_exists; then
        print_error "Service not installed. Run: sudo $0 install"
        exit 1
    fi
    
    sudo journalctl -u "$SERVICE_NAME" --no-pager -n 50
}

# Function to follow logs
follow_logs() {
    print_header "Following Service Logs (Press Ctrl+C to stop)"
    
    if ! service_exists; then
        print_error "Service not installed. Run: sudo $0 install"
        exit 1
    fi
    
    sudo journalctl -u "$SERVICE_NAME" -f
}

# Function to enable service
enable_service() {
    print_header "Enabling Auto-Start"
    
    if ! service_exists; then
        print_error "Service not installed. Run: sudo $0 install"
        exit 1
    fi
    
    print_status "Enabling service for auto-start..."
    sudo systemctl enable "$SERVICE_NAME"
    
    print_status "✅ Service enabled for auto-start!"
}

# Function to disable service
disable_service() {
    print_header "Disabling Auto-Start"
    
    if ! service_exists; then
        print_error "Service not installed. Run: sudo $0 install"
        exit 1
    fi
    
    print_status "Disabling service auto-start..."
    sudo systemctl disable "$SERVICE_NAME"
    
    print_status "✅ Service auto-start disabled!"
}

# Function to install service
install_service() {
    print_header "Installing Service"
    
    if [ "$EUID" -ne 0 ]; then
        print_error "Installation requires root privileges. Use: sudo $0 install"
        exit 1
    fi
    
    if [ -f "install-service.sh" ]; then
        ./install-service.sh
    else
        print_error "install-service.sh not found!"
        exit 1
    fi
}

# Function to uninstall service
uninstall_service() {
    print_header "Uninstalling Service"
    
    if [ "$EUID" -ne 0 ]; then
        print_error "Uninstallation requires root privileges. Use: sudo $0 uninstall"
        exit 1
    fi
    
    if [ -f "uninstall-service.sh" ]; then
        ./uninstall-service.sh
    else
        print_error "uninstall-service.sh not found!"
        exit 1
    fi
}

# Main script logic
case "${1:-help}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    follow)
        follow_logs
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    install)
        install_service
        ;;
    uninstall)
        uninstall_service
        ;;
    help|*)
        show_usage
        ;;
esac
