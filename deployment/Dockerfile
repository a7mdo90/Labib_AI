FROM python:3.11-slim

WORKDIR /app

# Install system dependencies required for PyMuPDF and other packages
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libmupdf-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libopenjp2-7-dev \
    zlib1g-dev \
    wget \
&& rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY ../scripts/requirements.txt .

# Install Python packages with specific handling for PyMuPDF
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir PyMuPDF==1.23.7 && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY ../src ./src
COPY ../config ./config
COPY ../data ./data

# Create necessary directories
RUN mkdir -p logs

CMD ["python3", "src/labib_bot.py", "--mode", "bot"]