# Use the official Python 3.12 slim image
FROM python:3.12-slim AS builder

# Set working directory inside the container
WORKDIR /smart-canvas

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip and set up dependency cache
RUN pip install --upgrade pip

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies with caching enabled
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project AFTER dependencies are installed
COPY . .

# Set Flask environment variables
ENV FLASK_APP=web
ENV FLASK_ENV=development

# Expose Flask's default port
EXPOSE 5000

# Run Flask (replace with gunicorn if deploying to production)
CMD ["flask", "run", "--host=0.0.0.0"]