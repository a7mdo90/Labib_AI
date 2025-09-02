#!/bin/bash

# Labib Telegram Bot Stop Script
# This script stops the bot using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [STOP]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

# Change to bot directory
cd /opt/labib-bot

print_status "Stopping Labib Telegram Bot..."

# Stop the bot
print_status "Stopping bot container..."
docker-compose -f docker-compose.prod.yml down

# Log the shutdown
echo "$(date '+%Y-%m-%d %H:%M:%S') - Bot stopped" >> logs/service.log

print_status "✅ Bot stopped successfully!"

exit 0
