FROM python:3.11-slim

# Install system dependencies (FFmpeg is here!)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libffi-dev \
    libnacl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Install python libraries
RUN pip install --no-cache-dir discord.py[voice] PyNaCl

# Start the bot
CMD ["python", "bot.py"]
