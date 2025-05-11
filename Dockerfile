FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    wget \
    curl \
    chromium \
    chromium-driver \
    libgconf-2-4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxrandr2 \
    libglu1-mesa \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

ENV CHROME_BIN=/usr/bin/chromium
ENV DISPLAY=:99

COPY . /app/

EXPOSE 8000
