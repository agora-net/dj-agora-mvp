# Multi-stage Dockerfile for Django + React application
# Stage 1: Frontend build stage
FROM node:24-slim AS frontend-builder
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# Set working directory for frontend
# Use a long path because the tailwind.css needs to be able to walk up
# @import "tailwindcss" source("../../../../");
WORKDIR /app/agora/frontend/@agora/agora

# Copy frontend package files
COPY frontend/@agora/agora/package.json frontend/@agora/agora/pnpm-lock.yaml ./

# Install pnpm and dependencies
# RUN npm install -g pnpm
RUN pnpm install --frozen-lockfile

# Copy frontend source code
COPY frontend/@agora/agora/ ./

# Build frontend assets
RUN pnpm build

# Stage 2: Python dependencies stage
FROM python:3.13-slim AS python-deps

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy Python dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Stage 3: Production stage
FROM python:3.13-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy Python dependencies from previous stage
COPY --from=python-deps /app/.venv /app/.venv

# Copy application code
COPY . .

# Copy built frontend assets from frontend-builder stage
COPY --from=frontend-builder /app/agora/frontend/@agora/agora/dist /app/frontend/@agora/agora/dist

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV DJANGO_SETTINGS_MODULE="agora.settings"
ENV SECRET_KEY="dummy_insecure_pae2eikie4oodohGooPai8eiShixai0o"

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media

# Collect static files
RUN /app/.venv/bin/python manage.py collectstatic --noinput

# Change ownership to non-root user
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

# Default command
CMD ["/app/.venv/bin/gunicorn", "--config", "config/gunicorn/gunicorn.conf.py", "agora.wsgi:application"]
