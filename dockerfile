# Multi-stage build for production deployment
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app ./app
COPY .env.example .env

# Create necessary directories and set permissions
RUN mkdir -p /app/data /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000 5001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=10)" || exit 1

# Create startup script
COPY --chown=appuser:appuser <<EOF /app/start.sh
#!/bin/bash
set -e

echo "Starting Book Recommendation Engine..."

# Initialize database if it doesn't exist
python -c "
try:
    from app.db import init_db
    init_db()
    print('Database initialized successfully')
except Exception as e:
    print(f'Database initialization error: {e}')
"

# Start backend API in background
echo "Starting backend API..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --proxy-headers &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "Backend failed to start"
        exit 1
    fi
    sleep 2
done

# Start frontend
echo "Starting frontend..."
python -c "
from app.frontend import create_flask_app
app = create_flask_app()
app.run(host='0.0.0.0', port=5001, debug=False)
" &
FRONTEND_PID=$!

# Function to handle shutdown
shutdown() {
    echo "Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap shutdown SIGTERM SIGINT

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
EOF

# Make startup script executable
USER root
RUN chmod +x /app/start.sh
USER appuser

# Default command
CMD ["/app/start.sh"]
