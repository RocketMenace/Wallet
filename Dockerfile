# Stage 1: Builder stage for dependency installation and building
FROM python:3.12-slim-bookworm AS builder

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.8.2 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR=/var/cache/pypoetry \
    POETRY_HOME=/opt/poetry

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH
ENV PATH="${POETRY_HOME}/bin:${PATH}"

# Set working directory
WORKDIR /app

# Copy only dependency files first for better layer caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies (without the main application) to system Python
RUN poetry install --only main --no-root --no-interaction

# Stage 2: Production stage
FROM python:3.12-slim-bookworm AS production

# Security best practices: Run as non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

# Install system dependencies required for runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    # For health checks and debugging
    curl \
    # For some Python packages that might need libpq, openssl, etc.
    libpq5 \
    openssl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory and set permissions
RUN mkdir -p /app && chown appuser:appuser /app
WORKDIR /app

# Copy installed dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy and make entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER appuser

# Copy application code
COPY --chown=appuser:appuser . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["/entrypoint.sh"]