#!/bin/bash

# Labib Telegram Bot Startup Script
# This script starts the bot using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] [START]${NC} $1"
}

print_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] [WARNING]${NC} $1"
}

# Change to bot directory
cd /opt/labib-bot

print_status "Starting Labib Telegram Bot..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Starting Docker service..."
    systemctl start docker
    sleep 10
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found!"
    exit 1
fi

# Check if vision-ocr-key.json exists
if [ ! -f vision-ocr-key.json ]; then
    print_error "vision-ocr-key.json not found!"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p backups

# Stop any existing containers
print_status "Stopping any existing containers..."
docker-compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true

# Start the bot
print_status "Starting bot container..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for container to be healthy
print_status "Waiting for container to be healthy..."
sleep 15

# Check if container is running
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_status "✅ Bot started successfully!"
    
    # Log the startup
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Bot started successfully" >> logs/service.log
    
    exit 0
else
    print_error "❌ Failed to start bot!"
    docker-compose -f docker-compose.prod.yml logs >> logs/service.log 2>&1
    exit 1
fi
