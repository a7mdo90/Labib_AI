#!/bin/bash

# Labib Telegram Bot Restart Script
# This script restarts the bot using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [RESTART]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

# Change to bot directory
cd /opt/labib-bot

print_status "Restarting Labib Telegram Bot..."

# Restart the bot
print_status "Restarting bot container..."
docker-compose -f docker-compose.prod.yml restart

# Wait for container to be healthy
print_status "Waiting for container to be healthy..."
sleep 15

# Check if container is running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_status "✅ Bot restarted successfully!"
    
    # Log the restart
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Bot restarted successfully" >> logs/service.log
    
    exit 0
else
    print_error "❌ Failed to restart bot!"
    docker-compose -f docker-compose.prod.yml logs >> logs/service.log 2>&1
    exit 1
fi
