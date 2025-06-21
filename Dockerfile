# 🌌 Kensho - AI Learning Assistant
# Multi-stage Docker build for Hugging Face deployment

# Stage 1: Build Frontend
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Python Backend with Frontend
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    ffmpeg \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY kensho/ ./kensho/
COPY *.py ./
COPY setup.py ./

# Copy built frontend from previous stage
COPY --from=frontend-build /app/frontend/out ./static

# Create directories for sessions and data
RUN mkdir -p sessions data

# Copy nginx configuration
COPY docker/nginx.conf /etc/nginx/sites-available/default

# Set environment variables for Hugging Face
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV HOST=0.0.0.0

# Expose port (Hugging Face uses 7860)
EXPOSE 7860

# Create startup script
RUN echo '#!/bin/bash\n\
# Start nginx for serving static files\n\
service nginx start\n\
\n\
# Start the FastAPI server\n\
exec python api_server.py --host 0.0.0.0 --port 7860\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Run the application
CMD ["/app/start.sh"] 