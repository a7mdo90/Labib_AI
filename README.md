# Labib Telegram Bot - Organized Structure

## 📁 Project Structure

```
Labib_telegram_bot/
├── main.py                 # Main entry point
├── deploy.py               # Deployment entry point
├── src/                    # Source code
│   ├── labib_bot.py       # Main bot (all-in-one)
│   ├── telegram_bot.py    # Original bot (backup)
│   ├── qa_engine.py       # Question answering engine
│   ├── config.py          # Configuration management
│   └── ocr_all_textbooks_to_chroma.py  # Original OCR (backup)
├── deployment/             # Deployment files
│   ├── deploy.py          # Deployment script
│   ├── Dockerfile         # Docker configuration
│   ├── docker-compose.yml # Docker Compose
│   └── labib-bot.service  # Systemd service
├── config/                 # Configuration files
│   ├── .env               # Environment variables
│   ├── env.example        # Environment template
│   └── vision-ocr-key.json # Google Vision API key
├── data/                   # Data storage
│   ├── chroma_store/      # ChromaDB database
│   ├── Textbook_pages/    # PDF textbooks
│   └── poppler-24.08.0/   # PDF processing tools
├── docs/                   # Documentation
│   ├── README.md          # This file
│   ├── README_STREAMLINED.md
│   ├── PROJECT_SUMMARY.md
│   ├── TASK_LIST.md
│   ├── TASKS.md
│   └── CONVERSATION_LOG.txt
├── logs/                   # Log files
│   └── *.log              # All log files
└── scripts/                # Utility scripts
    └── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

### Run the Bot
```bash
# Run Telegram bot
python main.py --mode bot

# Process textbooks
python main.py --mode process

# Health check
python main.py --mode health

# Cleanup files
python main.py --mode cleanup
```

### Deploy the Bot
```bash
# Deploy with Docker
python deploy.py --mode docker

# Install systemd service (Linux)
python deploy.py --mode systemd

# Health check
python deploy.py --mode health

# Show status
python deploy.py --mode status
```

## 📋 Features

### Core Functionality
- ✅ **Telegram Bot**: Full Telegram bot with commands and message handling
- ✅ **OCR Processing**: PDF to text conversion using Google Vision API
- ✅ **Database**: ChromaDB vector database for semantic search
- ✅ **AI Integration**: OpenAI GPT for intelligent responses
- ✅ **Health Monitoring**: Comprehensive health checks
- ✅ **File Management**: Automatic cleanup and organization

### Deployment Options
- ✅ **Docker**: Containerized deployment
- ✅ **Systemd**: Linux service management
- ✅ **Cross-platform**: Windows, Linux, macOS support
- ✅ **Automated**: One-command deployment

## 🔧 Configuration

### Environment Variables
Copy `config/env.example` to `config/.env` and configure:

```bash
# Telegram Bot
TELEGRAM_TOKEN=your_telegram_token

# OpenAI API
OPENAI_API_KEY=your_openai_key

# Google Cloud Vision
GOOGLE_APPLICATION_CREDENTIALS=config/vision-ocr-key.json

# Database
CHROMA_DB_PATH=data/chroma_store
```

### API Keys Required
1. **Telegram Bot Token**: Get from @BotFather
2. **OpenAI API Key**: Get from OpenAI platform
3. **Google Vision API**: Download service account key

## 📊 Usage Examples

### Process Textbooks
```bash
python main.py --mode process
```

### Run Health Check
```bash
python main.py --mode health
```

### Deploy to Production
```bash
python deploy.py --mode docker
```

### Check Status
```bash
python deploy.py --mode status
```

## 🛠️ Development

### Adding New Features
1. Edit `src/labib_bot.py` for core functionality
2. Update `deployment/deploy.py` for deployment changes
3. Test with `python main.py --mode health`

### File Organization
- **`src/`**: All source code
- **`config/`**: Configuration files
- **`data/`**: Data storage and databases
- **`deployment/`**: Deployment scripts and configs
- **`docs/`**: Documentation
- **`logs/`**: Log files
- **`scripts/`**: Utility scripts

## 🚀 Production Deployment

### Docker Deployment
```bash
cd deployment
docker-compose up -d
```

### Systemd Service (Linux)
```bash
sudo python deploy.py --mode systemd
sudo systemctl start labib-bot
```

## 📝 Notes

- All functionality is preserved from the original project
- Organized structure makes maintenance easier
- Clear separation of concerns
- Production-ready deployment options
- Comprehensive logging and monitoring

---

**Author**: Labib AI Team  
**Date**: September 18, 2025  
**Version**: Organized v1.0
