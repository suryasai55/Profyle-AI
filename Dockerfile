# Use official lightweight Python base image
FROM python:3.12-slim

# Set environment variables to prevent Python from writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PORT=5000

# Set container working directory
WORKDIR /app

# Install system dependencies (e.g., build tools for cryptography if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first to utilize Docker layer caching
COPY requirements.txt /app/

# Install Python package dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/uploads /app/nltk_data /app/db

# Pre-download NLTK resources during build to make container bootstrap instant
RUN python -c "import nltk; nltk.download('punkt', download_dir='/app/nltk_data'); nltk.download('stopwords', download_dir='/app/nltk_data')"

# Copy application source code
COPY . /app/

# Expose port
EXPOSE 5000

# Run Gunicorn production server with 4 worker processes
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
