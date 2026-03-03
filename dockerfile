# Use a Python image
FROM python:3.11-slim

# Install FFmpeg and system tools
RUN apt-get update && apt-get install -y ffmpeg libffi-dev libnacl-dev python3-dev

# Set up the bot folder
WORKDIR /app
COPY . /app

# Install Python libraries
RUN pip install --no-cache-dir discord.py[voice] PyNaCl

# Start the bot
CMD ["python", "bot.py"]
