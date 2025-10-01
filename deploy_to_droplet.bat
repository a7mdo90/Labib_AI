@echo off
echo 🚀 Labib Bot Droplet Deployment
echo ===============================

set /p DROPLET_IP="Enter your droplet IP address: "
set /p DROPLET_USER="Enter your droplet username (default: root): "
if "%DROPLET_USER%"=="" set DROPLET_USER=root

echo.
echo 🔧 Deploying to: %DROPLET_USER%@%DROPLET_IP%
echo.

echo 📦 Preparing droplet environment...
ssh %DROPLET_USER%@%DROPLET_IP% "apt-get update -y && apt-get install -y git python3 python3-pip docker.io docker-compose && systemctl start docker && systemctl enable docker && mkdir -p /opt/labib-bot"

echo 📥 Cloning latest code...
ssh %DROPLET_USER%@%DROPLET_IP% "cd /opt/labib-bot && rm -rf Labib_AI && git clone https://github.com/a7mdo90/Labib_AI.git"

echo 🔧 Setting up bot...
ssh %DROPLET_USER%@%DROPLET_IP% "cd /opt/labib-bot/Labib_AI && mkdir -p data/chroma_store logs config && cp config/env.example config/.env"

echo 🐳 Building and starting Docker...
ssh %DROPLET_USER%@%DROPLET_IP% "cd /opt/labib-bot/Labib_AI/deployment && docker-compose build && docker-compose up -d"

echo 🔄 Setting up auto-start service...
ssh %DROPLET_USER%@%DROPLET_IP% "cd /opt/labib-bot/Labib_AI/deployment && sudo cp labib-bot.service /etc/systemd/system/ && sudo systemctl daemon-reload && sudo systemctl enable labib-bot.service"

echo 📊 Checking status...
ssh %DROPLET_USER%@%DROPLET_IP% "cd /opt/labib-bot/Labib_AI/deployment && docker-compose ps"

echo.
echo ✅ Deployment completed!
echo.
echo 📋 Next steps:
echo 1. SSH to your droplet: ssh %DROPLET_USER%@%DROPLET_IP%
echo 2. Edit config: nano /opt/labib-bot/Labib_AI/config/.env
echo 3. Upload vision key: scp vision-ocr-key.json %DROPLET_USER%@%DROPLET_IP%:/opt/labib-bot/Labib_AI/config/
echo 4. Restart bot: cd /opt/labib-bot/Labib_AI/deployment ^&^& docker-compose restart
echo.
echo 🤖 Your bot is now running live 24/7!
pause
