#!/bin/bash

# Labib Telegram Bot Droplet Deployment Script
# This script deploys the bot in an isolated Docker container

set -e

echo "🚀 Deploying Labib Telegram Bot to Droplet..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    print_error ".env file not found. Please create it from env.example first."
    exit 1
fi

# Check if vision-ocr-key.json exists
if [ ! -f vision-ocr-key.json ]; then
    print_error "vision-ocr-key.json not found. Please ensure your Google Cloud Vision credentials are present."
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Stop and remove existing container if it exists
print_status "Stopping existing container..."
docker-compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true

# Remove existing images to ensure fresh build
print_status "Removing old images..."
docker rmi labib_telegram_bot_labib_bot 2>/dev/null || true

# Build and start the container
print_status "Building and starting container..."
docker-compose -f docker-compose.prod.yml up -d --build

# Wait for container to be healthy
print_status "Waiting for container to be healthy..."
sleep 10

# Check container status
if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    print_status "✅ Bot deployed successfully!"
    
    # Show container info
    echo ""
    print_status "Container Information:"
    docker-compose -f docker-compose.prod.yml ps
    
    echo ""
    print_status "Container Logs:"
    docker-compose -f docker-compose.prod.yml logs --tail=20
    
    echo ""
    print_status "Useful Commands:"
    echo "  View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "  Stop bot: docker-compose -f docker-compose.prod.yml down"
    echo "  Restart bot: docker-compose -f docker-compose.prod.yml restart"
    echo "  Check status: docker-compose -f docker-compose.prod.yml ps"
    
else
    print_error "❌ Bot deployment failed!"
    echo ""
    print_status "Container Logs:"
    docker-compose -f docker-compose.prod.yml logs
    exit 1
fi
