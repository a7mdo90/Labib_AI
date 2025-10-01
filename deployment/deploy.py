#!/usr/bin/env python3
"""
Labib Bot Deployment Script
===========================

This script handles all deployment operations:
- Docker deployment
- Systemd service installation
- Environment setup
- Health checks
- Service management

Author: Labib AI Team
Date: September 18, 2025
"""

import os
import sys
import subprocess
import argparse
import platform
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('deployment.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LabibDeployer:
    """Main deployment class."""
    
    def __init__(self):
        """Initialize the deployer."""
        self.platform = platform.system().lower()
        self.is_windows = self.platform == 'windows'
        self.is_linux = self.platform == 'linux'
        self.project_root = Path(".")
        
    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met."""
        logger.info("Checking prerequisites...")
        
        prerequisites = {
            'config/vision-ocr-key.json': 'Google Cloud Vision API key file',
            'config/.env': 'Environment variables file',
            'src/labib_bot.py': 'Main bot script',
            'scripts/requirements.txt': 'Python dependencies file',
            'deployment/Dockerfile': 'Docker configuration'
        }
        
        missing_files = []
        
        for file_path, description in prerequisites.items():
            if not (self.project_root / file_path).exists():
                missing_files.append(f"Missing: {file_path} - {description}")
            else:
                logger.info(f"Found: {file_path} - {description}")
        
        if missing_files:
            logger.error("Missing prerequisites:")
            for missing in missing_files:
                logger.error(f"   {missing}")
            return False
        
        # Check Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Docker: {result.stdout.strip()}")
            else:
                logger.error("Docker not found or not running")
                return False
        except FileNotFoundError:
            logger.error("Docker not installed")
            return False
        
        logger.info("All prerequisites met!")
        return True
    
    def create_docker_compose(self) -> str:
        """Create Docker Compose configuration."""
        docker_compose_content = """version: '3.8'

services:
  labib_bot:
    build: .
    container_name: labib_telegram_bot
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - "./chroma_store:/app/chroma_store:rw"
      - "./logs:/app/logs:rw"
      - "./vision-ocr-key.json:/app/vision-ocr-key.json:ro"
    env_file:
      - .env
    environment:
      - CHROMA_DB_PATH=/app/chroma_store
      - LOG_LEVEL=INFO
      - ENVIRONMENT=production
      - PYTHONUNBUFFERED=1
    networks:
      - labib_network
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  labib_network:
    driver: bridge
"""
        
        compose_file = self.project_root / "deployment" / "docker-compose.yml"
        with open(compose_file, 'w', encoding='utf-8') as f:
            f.write(docker_compose_content)
        
        logger.info(f"Created Docker Compose file: {compose_file}")
        return str(compose_file)
    
    def create_systemd_service(self) -> str:
        """Create systemd service file."""
        service_content = """[Unit]
Description=Labib Telegram Bot Service
Documentation=https://github.com/a7mdo90/Labib_AI
After=docker.service
Requires=docker.service
StartLimitInterval=0

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/labib-bot
ExecStart=/opt/labib-bot/start-bot.sh
ExecStop=/opt/labib-bot/stop-bot.sh
ExecReload=/opt/labib-bot/restart-bot.sh
TimeoutStartSec=300
TimeoutStopSec=60
Restart=on-failure
RestartSec=30
User=root
Group=root

# Environment variables
Environment=HOME=/opt/labib-bot
Environment=PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/labib-bot/chroma_store /opt/labib-bot/logs /opt/labib-bot/backups

[Install]
WantedBy=multi-user.target
"""
        
        service_file = self.project_root / "deployment" / "labib-bot.service"
        with open(service_file, 'w', encoding='utf-8') as f:
            f.write(service_content)
        
        logger.info(f"Created systemd service file: {service_file}")
        return str(service_file)
    
    def create_start_script(self) -> str:
        """Create start script."""
        start_script_content = """#!/bin/bash

# Labib Telegram Bot Startup Script
set -e

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Labib Telegram Bot..."

# Change to bot directory
cd /opt/labib-bot

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "[ERROR] Docker is not running. Starting Docker service..."
    systemctl start docker
    sleep 10
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "[ERROR] .env file not found!"
    exit 1
fi

# Check if vision-ocr-key.json exists
if [ ! -f vision-ocr-key.json ]; then
    echo "[ERROR] vision-ocr-key.json not found!"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the bot using Docker Compose
echo "[INFO] Starting bot container..."
docker-compose up -d --build

# Wait for container to be healthy
echo "[INFO] Waiting for container to be healthy..."
sleep 15

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo "[SUCCESS] Bot started successfully!"
    
    # Log the startup
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Bot started" >> logs/service.log
    
    exit 0
else
    echo "[ERROR] Bot failed to start!"
    docker-compose logs
    exit 1
fi
"""
        
        start_file = self.project_root / "deployment" / "start-bot.sh"
        with open(start_file, 'w', encoding='utf-8') as f:
            f.write(start_script_content)
        
        # Make executable on Unix systems
        if not self.is_windows:
            os.chmod(start_file, 0o755)
        
        logger.info(f"Created start script: {start_file}")
        return str(start_file)
    
    def create_stop_script(self) -> str:
        """Create stop script."""
        stop_script_content = """#!/bin/bash

# Labib Telegram Bot Stop Script
set -e

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Stopping Labib Telegram Bot..."

# Change to bot directory
cd /opt/labib-bot

# Stop the bot
echo "[INFO] Stopping bot container..."
docker-compose down

# Log the shutdown
echo "$(date '+%Y-%m-%d %H:%M:%S') - Bot stopped" >> logs/service.log

echo "[SUCCESS] Bot stopped successfully!"

exit 0
"""
        
        stop_file = self.project_root / "deployment" / "stop-bot.sh"
        with open(stop_file, 'w', encoding='utf-8') as f:
            f.write(stop_script_content)
        
        # Make executable on Unix systems
        if not self.is_windows:
            os.chmod(stop_file, 0o755)
        
        logger.info(f"Created stop script: {stop_file}")
        return str(stop_file)
    
    def create_restart_script(self) -> str:
        """Create restart script."""
        restart_script_content = """#!/bin/bash

# Labib Telegram Bot Restart Script
set -e

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Restarting Labib Telegram Bot..."

# Change to bot directory
cd /opt/labib-bot

# Restart the bot
echo "[INFO] Restarting bot container..."
docker-compose restart

# Wait for container to be healthy
echo "[INFO] Waiting for container to be healthy..."
sleep 15

# Check if container is running
if docker-compose ps | grep -q "Up"; then
    echo "[SUCCESS] Bot restarted successfully!"
    
    # Log the restart
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Bot restarted" >> logs/service.log
    
    exit 0
else
    echo "[ERROR] Bot failed to restart!"
    docker-compose logs
    exit 1
fi
"""
        
        restart_file = self.project_root / "deployment" / "restart-bot.sh"
        with open(restart_file, 'w', encoding='utf-8') as f:
            f.write(restart_script_content)
        
        # Make executable on Unix systems
        if not self.is_windows:
            os.chmod(restart_file, 0o755)
        
        logger.info(f"Created restart script: {restart_file}")
        return str(restart_file)
    
    def deploy_docker(self) -> bool:
        """Deploy using Docker."""
        logger.info("Deploying with Docker...")
        
        try:
            # Create Docker Compose file
            self.create_docker_compose()
            
            # Build and start
            logger.info("Building Docker image...")
            result = subprocess.run(['docker-compose', 'build'], check=True, capture_output=True, text=True)
            logger.info("Docker image built successfully")
            
            logger.info("Starting containers...")
            result = subprocess.run(['docker-compose', 'up', '-d'], check=True, capture_output=True, text=True)
            logger.info("Containers started successfully")
            
            # Check status
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
            logger.info(f"Container status:\n{result.stdout}")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Docker deployment failed: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Docker deployment error: {e}")
            return False
    
    def install_systemd_service(self) -> bool:
        """Install systemd service."""
        if self.is_windows:
            logger.error("Systemd service installation is only available on Linux")
            return False
        
        logger.info("Installing systemd service...")
        
        try:
            # Create service files
            self.create_systemd_service()
            self.create_start_script()
            self.create_stop_script()
            self.create_restart_script()
            
            # Install service
            install_dir = "/opt/labib-bot"
            
            logger.info(f"Installing to {install_dir}...")
            
            # Copy files to installation directory
            subprocess.run(['sudo', 'mkdir', '-p', install_dir], check=True)
            subprocess.run(['sudo', 'cp', '-r', '.', f"{install_dir}/"], check=True)
            subprocess.run(['sudo', 'cp', 'labib-bot.service', '/etc/systemd/system/'], check=True)
            
            # Reload systemd
            subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
            
            # Enable service
            subprocess.run(['sudo', 'systemctl', 'enable', 'labib-bot.service'], check=True)
            
            logger.info("Systemd service installed successfully!")
            logger.info("Use 'sudo systemctl start labib-bot' to start the service")
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Systemd installation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Systemd installation error: {e}")
            return False
    
    def run_health_check(self) -> bool:
        """Run health check."""
        logger.info("Running health check...")
        
        try:
            # Import and run health check from main bot
            from labib_bot import LabibBot
            
            bot = LabibBot()
            success = bot.health_check()
            
            if success:
                logger.info("Health check passed!")
                return True
            else:
                logger.error("Health check failed!")
                return False
                
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False
    
    def cleanup_files(self):
        """Clean up deployment files."""
        logger.info("Cleaning up deployment files...")
        
        cleanup_patterns = [
            "temp_*.png",
            "temp_*.jpg",
            "temp_*.ogg",
            "temp_*.wav",
            "temp_page_*.png",
            "*.log",
            "*.tmp"
        ]
        
        cleaned_count = 0
        for pattern in cleanup_patterns:
            for file_path in self.project_root.glob(pattern):
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove {file_path}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} files")
    
    def show_status(self):
        """Show deployment status."""
        logger.info("Deployment Status:")
        
        # Check Docker containers
        try:
            result = subprocess.run(['docker-compose', 'ps'], capture_output=True, text=True)
            logger.info(f"Docker containers:\n{result.stdout}")
        except Exception as e:
            logger.warning(f"Could not check Docker status: {e}")
        
        # Check systemd service (Linux only)
        if self.is_linux:
            try:
                result = subprocess.run(['systemctl', 'status', 'labib-bot.service'], capture_output=True, text=True)
                logger.info(f"Systemd service:\n{result.stdout}")
            except Exception as e:
                logger.warning(f"Could not check systemd status: {e}")

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Labib Bot Deployment Script")
    parser.add_argument("--mode", choices=["docker", "systemd", "health", "cleanup", "status"], default="docker",
                       help="Deployment mode: docker, systemd, health, cleanup, status")
    parser.add_argument("--install-service", action="store_true", help="Install systemd service")
    
    args = parser.parse_args()
    
    try:
        deployer = LabibDeployer()
        
        # Check prerequisites
        if not deployer.check_prerequisites():
            logger.error("Prerequisites check failed!")
            return 1
        
        if args.mode == "docker":
            success = deployer.deploy_docker()
        elif args.mode == "systemd":
            success = deployer.install_systemd_service()
        elif args.mode == "health":
            success = deployer.run_health_check()
        elif args.mode == "cleanup":
            deployer.cleanup_files()
            success = True
        elif args.mode == "status":
            deployer.show_status()
            success = True
        
        if success:
            logger.info("Deployment completed successfully!")
            return 0
        else:
            logger.error("Deployment failed!")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Deployment interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Deployment failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
