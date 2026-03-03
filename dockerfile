# Use a Python base image
FROM python:3.11-slim

# 🛠️ Force-install FFmpeg into the OS
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libffi-dev \
    libnacl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the folder
WORKDIR /app
COPY . /app

# Install libraries
RUN pip install --no-cache-dir discord.py[voice] PyNaCl

# Start command
CMD ["python", "bot.py"]
