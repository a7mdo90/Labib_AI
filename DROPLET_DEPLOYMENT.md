# 🚀 Labib Telegram Bot - Droplet Deployment Guide

This guide will help you deploy the Labib Telegram Bot on your droplet/server without interfering with other services.

## 🏗️ Architecture

The bot runs in an **isolated Docker container** with:
- **Isolated network**: `labib_bot_network` (bridge driver)
- **Resource limits**: 1GB RAM, 0.5 CPU cores max
- **Persistent storage**: ChromaDB and logs mounted as volumes
- **Health monitoring**: Built-in health checks
- **Logging**: Rotated log files with size limits

### 🚀 System Service Benefits

When installed as a systemd service:
- **Auto-start on boot**: Bot starts automatically when server reboots
- **Independent of Docker Desktop**: Runs even when Docker Desktop is closed
- **System-level management**: Use standard Linux service commands
- **Automatic restart**: Service restarts automatically if it fails
- **Centralized logging**: All logs go to systemd journal
- **Production ready**: Designed for 24/7 operation

## 📋 Prerequisites

1. **Docker & Docker Compose** installed on your droplet
2. **Git** for pulling updates
3. **Port 8000** available (for health checks, optional)

## 🚀 Quick Deployment

### Option 1: Install as System Service (Recommended for Production)

This option installs the bot as a systemd service that starts automatically on server boot and runs independently of Docker Desktop.

```bash
# Make scripts executable
chmod +x *.sh

# Install as system service (requires sudo)
sudo ./install-service.sh

# Start the service
sudo systemctl start labib-bot

# Check status
sudo systemctl status labib-bot
```

### Option 2: Using the deployment script (Manual Control)

```bash
# Make scripts executable
chmod +x deploy_droplet.sh manage_bot.sh

# Deploy the bot
./deploy_droplet.sh
```

### Option 3: Manual deployment

```bash
# Build and start the container
docker-compose -f docker-compose.prod.yml up -d --build

# Check status
docker-compose -f docker-compose.prod.yml ps
```

## 🎮 Bot Management

### For System Service (Recommended)

Use the service manager for systemd service control:

```bash
# Show all available commands
./service-manager.sh help

# Start the service
sudo ./service-manager.sh start

# Stop the service
sudo ./service-manager.sh stop

# Restart the service
sudo ./service-manager.sh restart

# Check service status
./service-manager.sh status

# View service logs
./service-manager.sh logs

# Follow service logs in real-time
./service-manager.sh follow

# Enable auto-start on boot
sudo ./service-manager.sh enable

# Disable auto-start
sudo ./service-manager.sh disable
```

### For Manual Docker Management

Use the management script for Docker container control:

```bash
# Show all available commands
./manage_bot.sh help

# Start the bot
./manage_bot.sh start

# Stop the bot
./manage_bot.sh stop

# Restart the bot
./manage_bot.sh restart

# Check status
./manage_bot.sh status

# View logs
./manage_bot.sh logs

# Follow logs in real-time
./manage_bot.sh follow

# Deploy updates
./manage_bot.sh deploy

# Health check
./manage_bot.sh health

# Access container shell
./manage_bot.sh shell

# Backup data
./manage_bot.sh backup
```

## 🔧 Configuration

### Environment Variables
The bot uses your `.env` file for configuration. Ensure it contains:
- `TELEGRAM_TOKEN` - Your bot token from @BotFather
- `OPENAI_API_KEY` - Your OpenAI API key
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to vision-ocr-key.json

### File Structure
```
your-droplet/
├── Labib_telegram_bot/          # Bot directory
│   ├── docker-compose.prod.yml  # Production compose file
│   ├── manage_bot.sh           # Management script
│   ├── deploy_droplet.sh       # Deployment script
│   ├── .env                    # Environment variables
│   ├── vision-ocr-key.json     # Google Cloud credentials
│   ├── chroma_store/           # Database (mounted volume)
│   └── logs/                   # Log files (mounted volume)
```

## 📊 Monitoring

### Container Status
```bash
# Check if running
docker-compose -f docker-compose.prod.yml ps

# View resource usage
docker stats labib_telegram_bot
```

### Logs
```bash
# Recent logs
docker-compose -f docker-compose.prod.yml logs --tail=50

# Follow logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Health Checks
The container includes built-in health checks that run every 30 seconds.

## 🔄 Updates & Maintenance

### Pull Latest Changes
```bash
cd Labib_telegram_bot
git pull origin master
./manage_bot.sh deploy
```

### Backup Data
```bash
./manage_bot.sh backup
```
This creates timestamped backups in the `backups/` directory.

### Restart Services
```bash
# Restart just the bot
./manage_bot.sh restart

# Or restart Docker service (if needed)
sudo systemctl restart docker
```

## 🛠️ Troubleshooting

### Bot Won't Start
1. Check Docker status: `sudo systemctl status docker`
2. Check logs: `./manage_bot.sh logs`
3. Verify .env file exists and has correct values
4. Ensure vision-ocr-key.json is present

### Bot Not Responding
1. Check if container is running: `./manage_bot.sh status`
2. Verify Telegram token is correct
3. Check OpenAI API key validity
4. View real-time logs: `./manage_bot.sh follow`

### Resource Issues
1. Check memory usage: `docker stats`
2. Restart container: `./manage_bot.sh restart`
3. Check system resources: `htop` or `top`

### Network Issues
1. Check container network: `docker network ls`
2. Verify port availability: `netstat -tulpn | grep 8000`
3. Check firewall settings

## 🔒 Security Features

- **Isolated network**: Bot runs in its own network namespace
- **Resource limits**: Prevents resource exhaustion
- **Read-only credentials**: Google Cloud credentials mounted as read-only
- **Log rotation**: Prevents log file bloat
- **Health monitoring**: Automatic failure detection

## 📈 Scaling

The current setup is designed for single-instance deployment. For scaling:

1. **Load Balancing**: Add a reverse proxy (nginx/traefik)
2. **Multiple Instances**: Use Docker Swarm or Kubernetes
3. **Database**: Move ChromaDB to external database
4. **Monitoring**: Add Prometheus/Grafana for metrics

## 🆘 Support

If you encounter issues:

1. Check the logs: `./manage_bot.sh logs`
2. Verify configuration: `./manage_bot.sh health`
3. Restart the service: `./manage_bot.sh restart`
4. Check system resources: `./manage_bot.sh status`

## 🎯 Next Steps

After successful deployment:

1. **Test the bot**: Send a message on Telegram
2. **Monitor performance**: Use `./manage_bot.sh status`
3. **Set up monitoring**: Consider adding external monitoring
4. **Automate updates**: Set up cron jobs for automatic updates
5. **Backup strategy**: Schedule regular backups

---

**Happy Botting! 🤖✨**
