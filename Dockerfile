# Using a slim Python 3.12 image for a small footprint
FROM python:3.13-slim


# Install/upgrade system dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Prevent Python from buffering logs (so you see them in 'docker logs' instantly)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your source code
COPY ./observer ./observer

# No CMD -- defined in docker-compose.yml