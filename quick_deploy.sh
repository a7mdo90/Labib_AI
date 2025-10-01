#!/bin/bash

# Quick Droplet Deployment Script
# Run this script to deploy your bot to the droplet

echo "🚀 Quick Labib Bot Deployment to Droplet"
echo "========================================"

# Replace with your actual droplet IP
DROPLET_IP="YOUR_DROPLET_IP"
DROPLET_USER="root"

echo "📋 Please provide your droplet details:"
read -p "Enter your droplet IP address: " DROPLET_IP
read -p "Enter your droplet username (default: root): " DROPLET_USER
DROPLET_USER=${DROPLET_USER:-root}

echo ""
echo "🔧 Deploying to: $DROPLET_USER@$DROPLET_IP"
echo ""

# Step 1: Prepare droplet
echo "📦 Preparing droplet environment..."
ssh $DROPLET_USER@$DROPLET_IP << 'EOF'
    echo "Installing required packages..."
    apt-get update -y
    apt-get install -y git python3 python3-pip docker.io docker-compose
    
    echo "Starting Docker..."
    systemctl start docker
    systemctl enable docker
    
    echo "Creating deployment directory..."
    mkdir -p /opt/labib-bot
    cd /opt/labib-bot
EOF

# Step 2: Clone and setup
echo "📥 Cloning latest code..."
ssh $DROPLET_USER@$DROPLET_IP << 'EOF'
    cd /opt/labib-bot
    
    echo "Removing old deployment..."
    rm -rf Labib_AI
    
    echo "Cloning from GitHub..."
    git clone https://github.com/a7mdo90/Labib_AI.git
    cd Labib_AI
    
    echo "Creating directories..."
    mkdir -p data/chroma_store logs config
    
    echo "Setting up environment..."
    cp config/env.example config/.env
    
    echo "Building Docker image..."
    cd deployment
    docker-compose build
    
    echo "Starting bot..."
    docker-compose up -d
    
    echo "Setting up auto-start service..."
    sudo cp labib-bot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable labib-bot.service
    
    echo "Checking status..."
    docker-compose ps
EOF

echo ""
echo "✅ Deployment completed!"
echo ""
echo "📋 Next steps:"
echo "1. SSH to your droplet: ssh $DROPLET_USER@$DROPLET_IP"
echo "2. Edit config: nano /opt/labib-bot/Labib_AI/config/.env"
echo "3. Upload vision key: scp vision-ocr-key.json $DROPLET_USER@$DROPLET_IP:/opt/labib-bot/Labib_AI/config/"
echo "4. Restart bot: cd /opt/labib-bot/Labib_AI/deployment && docker-compose restart"
echo ""
echo "🤖 Your bot is now running live 24/7!"
