#!/bin/bash

# Labib Bot Droplet Deployment Script
# This script deploys the bot to your droplet for 24/7 operation

set -e

echo "🚀 Starting Labib Bot Droplet Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DROPLET_IP="YOUR_DROPLET_IP_HERE"
DROPLET_USER="root"
PROJECT_NAME="Labib_AI"
DEPLOY_DIR="/opt/labib-bot"

echo -e "${BLUE}📋 Deployment Configuration:${NC}"
echo "Droplet IP: $DROPLET_IP"
echo "User: $DROPLET_USER"
echo "Project: $PROJECT_NAME"
echo "Deploy Directory: $DEPLOY_DIR"
echo ""

# Check if droplet IP is configured
if [ "$DROPLET_IP" = "YOUR_DROPLET_IP_HERE" ]; then
    echo -e "${RED}❌ Please configure your droplet IP in this script first!${NC}"
    echo "Edit deploy_to_droplet.sh and replace YOUR_DROPLET_IP_HERE with your actual droplet IP"
    exit 1
fi

echo -e "${YELLOW}🔧 Step 1: Connecting to droplet and preparing environment...${NC}"

# SSH to droplet and prepare environment
ssh $DROPLET_USER@$DROPLET_IP << 'EOF'
    echo "📦 Installing required packages..."
    apt-get update
    apt-get install -y git python3 python3-pip docker.io docker-compose
    
    echo "🐳 Starting Docker service..."
    systemctl start docker
    systemctl enable docker
    
    echo "📁 Creating deployment directory..."
    mkdir -p /opt/labib-bot
    cd /opt/labib-bot
    
    echo "🗑️ Cleaning up any existing deployment..."
    rm -rf Labib_AI
EOF

echo -e "${YELLOW}🔧 Step 2: Uploading project files to droplet...${NC}"

# Create a temporary archive of the project
echo "📦 Creating project archive..."
tar -czf labib_bot_deployment.tar.gz \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs/*.log' \
    --exclude='data/chroma_store' \
    --exclude='data/Textbook_pages' \
    --exclude='data/poppler-24.08.0' \
    .

# Upload to droplet
echo "📤 Uploading to droplet..."
scp labib_bot_deployment.tar.gz $DROPLET_USER@$DROPLET_IP:/opt/labib-bot/

# Clean up local archive
rm labib_bot_deployment.tar.gz

echo -e "${YELLOW}🔧 Step 3: Setting up bot on droplet...${NC}"

# SSH to droplet and setup
ssh $DROPLET_USER@$DROPLET_IP << 'EOF'
    cd /opt/labib-bot
    
    echo "📂 Extracting project files..."
    tar -xzf labib_bot_deployment.tar.gz
    rm labib_bot_deployment.tar.gz
    
    echo "📥 Cloning latest code from GitHub..."
    rm -rf Labib_AI
    git clone https://github.com/a7mdo90/Labib_AI.git
    cd Labib_AI
    
    echo "🔧 Setting up environment..."
    # Create necessary directories
    mkdir -p data/chroma_store
    mkdir -p logs
    mkdir -p config
    
    # Copy environment file
    if [ ! -f config/.env ]; then
        cp config/env.example config/.env
        echo "⚠️  Please edit config/.env with your actual API keys!"
    fi
    
    # Copy vision key if it exists locally
    if [ -f config/vision-ocr-key.json ]; then
        echo "✅ Vision API key found"
    else
        echo "⚠️  Please upload your vision-ocr-key.json to config/ directory"
    fi
    
    echo "🐳 Building Docker image..."
    cd deployment
    docker-compose build
    
    echo "🚀 Starting bot service..."
    docker-compose up -d
    
    echo "⏳ Waiting for bot to start..."
    sleep 10
    
    echo "📊 Checking bot status..."
    docker-compose ps
    
    echo "📝 Setting up systemd service for auto-start..."
    sudo cp labib-bot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable labib-bot.service
    
    echo "✅ Bot deployment completed!"
EOF

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo "1. SSH to your droplet: ssh $DROPLET_USER@$DROPLET_IP"
echo "2. Edit config file: nano /opt/labib-bot/Labib_AI/config/.env"
echo "3. Upload your vision-ocr-key.json to: /opt/labib-bot/Labib_AI/config/"
echo "4. Restart bot: cd /opt/labib-bot/Labib_AI/deployment && docker-compose restart"
echo ""
echo -e "${GREEN}🤖 Your bot is now running live 24/7 on your droplet!${NC}"
echo -e "${BLUE}📱 Test it by messaging your Telegram bot${NC}"
