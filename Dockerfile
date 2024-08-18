# Base Image
FROM python:3.12-slim-bookworm AS base

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Dependencies Stage
FROM base AS dependencies

# Copy the requirements file to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Development Stage
FROM dependencies AS development

# Copy the application code
COPY . .

# Set permissions for the application code
RUN adduser --disabled-password --gecos '' appuser && \
  chown -R appuser:appuser /app && \
  chmod -R 755 /app

USER appuser

# Expose port
EXPOSE 8000

# Run the development server
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]

# Production Stage
FROM dependencies AS production

# Copy the application code
COPY . .

# Set permissions for the application code
RUN adduser --disabled-password --gecos '' appuser && \
  chown -R appuser:appuser /app && \
  chmod -R 755 /app

USER appuser

# Expose port
EXPOSE 8000

# Run Gunicorn for production
CMD ["gunicorn", "bigapi.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
