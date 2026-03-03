# Use a Python base image
FROM python:3.11-slim

# 🛠️ THIS IS THE FIX: Installs FFmpeg directly into the OS
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libffi-dev \
    libnacl-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working folder
WORKDIR /app
COPY . /app

# Install your bot's libraries
RUN pip install --no-cache-dir discord.py[voice] PyNaCl

# Start the bot
CMD ["python", "bot.py"]
