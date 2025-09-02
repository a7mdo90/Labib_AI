@echo off
REM Labib Telegram Bot Droplet Deployment Script for Windows
REM This script deploys the bot in an isolated Docker container

echo 🚀 Deploying Labib Telegram Bot to Droplet...

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found. Please create it from env.example first.
    pause
    exit /b 1
)

REM Check if vision-ocr-key.json exists
if not exist vision-ocr-key.json (
    echo [ERROR] vision-ocr-key.json not found. Please ensure your Google Cloud Vision credentials are present.
    pause
    exit /b 1
)

REM Create logs directory if it doesn't exist
if not exist logs mkdir logs

REM Stop and remove existing container if it exists
echo [INFO] Stopping existing container...
docker-compose -f docker-compose.prod.yml down --remove-orphans 2>nul

REM Remove existing images to ensure fresh build
echo [INFO] Removing old images...
docker rmi labib_telegram_bot_labib_bot 2>nul

REM Build and start the container
echo [INFO] Building and starting container...
docker-compose -f docker-compose.prod.yml up -d --build

REM Wait for container to be healthy
echo [INFO] Waiting for container to be healthy...
timeout /t 10 /nobreak >nul

REM Check container status
docker-compose -f docker-compose.prod.yml ps | findstr "Up" >nul
if errorlevel 1 (
    echo [ERROR] ❌ Bot deployment failed!
    echo.
    echo [INFO] Container Logs:
    docker-compose -f docker-compose.prod.yml logs
    pause
    exit /b 1
) else (
    echo [INFO] ✅ Bot deployed successfully!
    
    REM Show container info
    echo.
    echo [INFO] Container Information:
    docker-compose -f docker-compose.prod.yml ps
    
    echo.
    echo [INFO] Container Logs:
    docker-compose -f docker-compose.prod.yml logs --tail=20
    
    echo.
    echo [INFO] Useful Commands:
    echo   View logs: docker-compose -f docker-compose.prod.yml logs -f
    echo   Stop bot: docker-compose -f docker-compose.prod.yml down
    echo   Restart bot: docker-compose -f docker-compose.prod.yml restart
    echo   Check status: docker-compose -f docker-compose.prod.yml ps
)

pause
