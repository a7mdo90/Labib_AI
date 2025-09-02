@echo off
REM Labib Telegram Bot Deployment Script for Windows
REM سكريبت نشر بوت تيليجرام لبيب لنظام ويندوز

echo 🚀 Starting Labib Bot deployment...

REM Check if .env file exists
if not exist .env (
    echo ❌ .env file not found. Please create it from env.example
    pause
    exit /b 1
)

REM Build and deploy
echo 🔨 Building Docker image...
docker-compose build

echo 📦 Starting services...
docker-compose up -d

echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check if bot is running
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ Labib Bot is running successfully!
    echo 📊 Check logs with: docker-compose logs -f labib_bot
) else (
    echo ❌ Deployment failed. Check logs:
    docker-compose logs labib_bot
    pause
    exit /b 1
)

echo 🎉 Deployment completed successfully!
pause
