# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set Poetry environment variables
ENV POETRY_HOME="/opt/poetry"
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false  # Install dependencies globally

# Set working directory inside the container
WORKDIR /smart-canvas

# Install system dependencies for Poetry & project
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 curl python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only dependency files first (to leverage Docker cache)
COPY pyproject.toml poetry.lock ./

# Install dependencies using Poetry
RUN poetry install --no-root --no-interaction --no-ansi

# Copy the rest of the project AFTER dependencies
COPY . .

# Set Flask environment variables
ENV FLASK_APP=web
ENV FLASK_ENV=development

# Expose Flask's default port
EXPOSE 5000

# Run Flask (or replace with gunicorn for production)
CMD ["poetry", "run", "gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "web:app"]
