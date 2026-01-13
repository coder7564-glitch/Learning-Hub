# Python base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . .

# Create directory for static files
RUN mkdir -p /app/staticfiles /app/media

# Expose port
EXPOSE 8000

# Run the application
CMD ["gunicorn", "lms_project.wsgi:application", "--bind", "0.0.0.0:8000"]
