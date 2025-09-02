# 🔧 Systemd Service Setup Guide

This guide will help you set up the Labib Telegram Bot as a systemd service that runs automatically on your server, independent of Docker Desktop.

## 🎯 Why Use Systemd Service?

- **🔄 Auto-start**: Bot starts automatically when server boots
- **🖥️ Independent**: Runs even when Docker Desktop is closed on your local machine
- **🛡️ Reliable**: Automatic restart if the service fails
- **📊 Centralized**: All logs go to systemd journal
- **⚡ Production**: Designed for 24/7 operation

## 🚀 Quick Setup

### Step 1: Install the Service

```bash
# Make scripts executable
chmod +x *.sh

# Install as system service (requires sudo)
sudo ./install-service.sh
```

### Step 2: Start the Service

```bash
# Start the bot service
sudo systemctl start labib-bot

# Check if it's running
sudo systemctl status labib-bot
```

### Step 3: Enable Auto-Start (Optional)

```bash
# Enable service to start automatically on boot
sudo systemctl enable labib-bot
```

## 🎮 Service Management

### Using the Service Manager (Recommended)

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
```

### Using Systemctl Commands

```bash
# Start service
sudo systemctl start labib-bot

# Stop service
sudo systemctl stop labib-bot

# Restart service
sudo systemctl restart labib-bot

# Check status
sudo systemctl status labib-bot

# View logs
sudo journalctl -u labib-bot -f

# Enable auto-start
sudo systemctl enable labib-bot

# Disable auto-start
sudo systemctl disable labib-bot
```

## 📊 Monitoring

### Check Service Status

```bash
# Quick status check
systemctl is-active labib-bot

# Detailed status
sudo systemctl status labib-bot

# Check if enabled for auto-start
systemctl is-enabled labib-bot
```

### View Logs

```bash
# Recent logs
sudo journalctl -u labib-bot --no-pager -n 50

# Follow logs in real-time
sudo journalctl -u labib-bot -f

# Logs from today
sudo journalctl -u labib-bot --since today
```

### Check Docker Container

```bash
# Check if Docker container is running
docker ps | grep labib

# View container logs
docker logs labib_telegram_bot
```

## 🔄 Updates

### Update the Bot

```bash
# Navigate to installation directory
cd /opt/labib-bot

# Pull latest changes
git pull origin master

# Restart the service to apply updates
sudo systemctl restart labib-bot
```

### Update Service Files

```bash
# Navigate to your project directory
cd /path/to/your/Labib_telegram_bot

# Pull latest changes
git pull origin master

# Reinstall the service
sudo ./install-service.sh
```

## 🛠️ Troubleshooting

### Service Won't Start

1. **Check service status**:
   ```bash
   sudo systemctl status labib-bot
   ```

2. **Check logs**:
   ```bash
   sudo journalctl -u labib-bot -n 50
   ```

3. **Check Docker**:
   ```bash
   sudo systemctl status docker
   ```

4. **Check files**:
   ```bash
   ls -la /opt/labib-bot/
   ```

### Service Keeps Restarting

1. **Check resource usage**:
   ```bash
   docker stats
   ```

2. **Check system resources**:
   ```bash
   htop
   ```

3. **Check logs for errors**:
   ```bash
   sudo journalctl -u labib-bot -f
   ```

### Bot Not Responding

1. **Check if container is running**:
   ```bash
   docker ps | grep labib
   ```

2. **Check container logs**:
   ```bash
   docker logs labib_telegram_bot
   ```

3. **Restart the service**:
   ```bash
   sudo systemctl restart labib-bot
   ```

## 🗑️ Uninstalling

### Remove the Service

```bash
# Uninstall the service
sudo ./uninstall-service.sh
```

This will:
- Stop and disable the service
- Remove systemd service file
- Optionally remove installation directory

## 📁 File Locations

After installation:

- **Service files**: `/etc/systemd/system/labib-bot.service`
- **Bot installation**: `/opt/labib-bot/`
- **Service logs**: `journalctl -u labib-bot`
- **Container logs**: `/opt/labib-bot/logs/`

## 🔒 Security Notes

- The service runs as root (required for Docker)
- Bot files are owned by root
- Service has restricted permissions
- Logs are accessible via systemd journal

## 🎯 Best Practices

1. **Enable auto-start** for production use
2. **Monitor logs** regularly for issues
3. **Update regularly** to get latest features
4. **Backup data** before major updates
5. **Test updates** in a staging environment first

---

**Your bot is now running as a system service! 🚀**

The bot will continue running even if you close Docker Desktop on your local machine, and it will automatically start when your server reboots.
