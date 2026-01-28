# Multi-stage Dockerfile for Flask Cache Server

# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create non-root user for security
RUN groupadd -r cacheuser && useradd -r -g cacheuser cacheuser

# Copy Python dependencies from builder stage
COPY --from=builder /root/.local /home/cacheuser/.local

# Copy application code
COPY app.py .
COPY config.py .

# Create cache directory and set permissions
RUN mkdir -p /app/cache_files && \
    chown -R cacheuser:cacheuser /app && \
    chmod -R 755 /app

# Switch to non-root user
USER cacheuser

# Add local bin to PATH
ENV PATH=/home/cacheuser/.local/bin:$PATH
ENV PYTHONPATH=/home/cacheuser/.local/lib/python3.11/site-packages:$PYTHONPATH

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start the application
CMD ["python", "app.py"]