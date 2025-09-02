#!/bin/bash

# Labib Telegram Bot Management Script
# Easy commands to manage the bot on your droplet

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

# Function to show usage
show_usage() {
    echo "Labib Telegram Bot Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start the bot"
    echo "  stop      - Stop the bot"
    echo "  restart   - Restart the bot"
    echo "  status    - Show bot status"
    echo "  logs      - Show bot logs"
    echo "  follow    - Follow bot logs in real-time"
    echo "  deploy    - Deploy/update the bot"
    echo "  health    - Check bot health"
    echo "  shell     - Access bot container shell"
    echo "  backup    - Backup bot data"
    echo "  help      - Show this help message"
    echo ""
}

# Function to check if container is running
is_running() {
    docker-compose -f docker-compose.prod.yml ps | grep -q "Up"
}

# Function to start bot
start_bot() {
    print_header "Starting Labib Telegram Bot"
    
    if is_running; then
        print_warning "Bot is already running!"
        return 1
    fi
    
    print_status "Starting bot container..."
    docker-compose -f docker-compose.prod.yml up -d
    
    sleep 5
    
    if is_running; then
        print_status "✅ Bot started successfully!"
    else
        print_error "❌ Failed to start bot!"
        docker-compose -f docker-compose.prod.yml logs
        return 1
    fi
}

# Function to stop bot
stop_bot() {
    print_header "Stopping Labib Telegram Bot"
    
    if ! is_running; then
        print_warning "Bot is not running!"
        return 1
    fi
    
    print_status "Stopping bot container..."
    docker-compose -f docker-compose.prod.yml down
    
    print_status "✅ Bot stopped successfully!"
}

# Function to restart bot
restart_bot() {
    print_header "Restarting Labib Telegram Bot"
    
    print_status "Restarting bot container..."
    docker-compose -f docker-compose.prod.yml restart
    
    sleep 5
    
    if is_running; then
        print_status "✅ Bot restarted successfully!"
    else
        print_error "❌ Failed to restart bot!"
        return 1
    fi
}

# Function to show status
show_status() {
    print_header "Bot Status"
    
    if is_running; then
        print_status "✅ Bot is RUNNING"
        echo ""
        docker-compose -f docker-compose.prod.yml ps
    else
        print_warning "⚠️  Bot is STOPPED"
    fi
    
    echo ""
    print_status "System Resources:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
}

# Function to show logs
show_logs() {
    print_header "Bot Logs (Last 50 lines)"
    docker-compose -f docker-compose.prod.yml logs --tail=50
}

# Function to follow logs
follow_logs() {
    print_header "Following Bot Logs (Press Ctrl+C to stop)"
    docker-compose -f docker-compose.prod.yml logs -f
}

# Function to deploy/update
deploy_bot() {
    print_header "Deploying/Updating Bot"
    
    print_status "Pulling latest changes..."
    git pull origin master
    
    print_status "Building and starting container..."
    docker-compose -f docker-compose.prod.yml up -d --build
    
    sleep 10
    
    if is_running; then
        print_status "✅ Bot deployed successfully!"
    else
        print_error "❌ Deployment failed!"
        docker-compose -f docker-compose.prod.yml logs
        return 1
    fi
}

# Function to check health
check_health() {
    print_header "Bot Health Check"
    
    if ! is_running; then
        print_error "❌ Bot is not running!"
        return 1
    fi
    
    print_status "Checking container health..."
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    print_status "Recent logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=10
}

# Function to access shell
access_shell() {
    print_header "Accessing Bot Container Shell"
    
    if ! is_running; then
        print_error "❌ Bot is not running!"
        return 1
    fi
    
    print_status "Opening shell in bot container..."
    docker-compose -f docker-compose.prod.yml exec labib_bot /bin/bash
}

# Function to backup data
backup_data() {
    print_header "Backing Up Bot Data"
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    print_status "Creating backup in $BACKUP_DIR..."
    
    # Backup ChromaDB
    if [ -d "chroma_store" ]; then
        cp -r chroma_store "$BACKUP_DIR/"
        print_status "✅ ChromaDB backed up"
    fi
    
    # Backup logs
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/"
        print_status "✅ Logs backed up"
    fi
    
    # Backup .env (without sensitive data)
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/"
        print_status "✅ Environment file backed up"
    fi
    
    print_status "✅ Backup completed in $BACKUP_DIR"
}

# Main script logic
case "${1:-help}" in
    start)
        start_bot
        ;;
    stop)
        stop_bot
        ;;
    restart)
        restart_bot
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
    deploy)
        deploy_bot
        ;;
    health)
        check_health
        ;;
    shell)
        access_shell
        ;;
    backup)
        backup_data
        ;;
    help|*)
        show_usage
        ;;
esac
