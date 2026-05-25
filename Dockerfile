FROM python:3.11-slim

# Install ffmpeg for music playback
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pythos_bot.py .

ENV PYTHONUNBUFFERED=1
EXPOSE 8080

CMD ["python", "pythos_bot.py"]
