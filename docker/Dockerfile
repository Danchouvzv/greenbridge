# Use Python 3.11 as base image
FROM python:3.11-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gdal-bin \
    libgdal-dev \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up a working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn==21.2.0

# Second stage: runtime environment
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    gdal-bin \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdal30 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up a working directory
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy project files
COPY . .

# Create non-root user for security
RUN groupadd -r django && useradd -r -g django django \
    && mkdir -p /app/staticfiles /app/media \
    && chown -R django:django /app

# Switch to non-root user
USER django

# Run entrypoint script
COPY ./docker/entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]

# Default command
CMD ["gunicorn", "greenbridge.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "4"] 