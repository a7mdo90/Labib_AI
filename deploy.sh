#!/bin/bash

# Labib Telegram Bot Deployment Script
# سكريبت نشر بوت تيليجرام لبيب

set -e

echo "🚀 Starting Labib Bot deployment..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it from env.example"
    exit 1
fi

# Build and deploy
echo "🔨 Building Docker image..."
docker-compose build

echo "📦 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check if bot is running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Labib Bot is running successfully!"
    echo "📊 Check logs with: docker-compose logs -f labib_bot"
else
    echo "❌ Deployment failed. Check logs:"
    docker-compose logs labib_bot
    exit 1
fi

echo "🎉 Deployment completed successfully!"
