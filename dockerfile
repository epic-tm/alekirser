FROM python:3.11-slim

# This is the magic line that fixes your error
RUN apt-get update && apt-get install -y ffmpeg libffi-dev libnacl-dev python3-dev

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir discord.py[voice] PyNaCl

CMD ["python", "bot.py"]
