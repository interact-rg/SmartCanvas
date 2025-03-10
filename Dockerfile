# Use the official Python 3.12 slim image
FROM python:3.12-slim

# Set Poetry environment variables
ENV POETRY_HOME="/opt/poetry"
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

# Set working directory inside the container
WORKDIR /smart-canvas

# Install system dependencies for Poetry & project
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 curl python3-venv && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy only dependency files first (to leverage Docker cache)
COPY pyproject.toml poetry.lock ./

# Install dependencies before copying the full project
RUN poetry install --no-root --no-interaction --no-ansi

# Now copy the rest of the project AFTER dependencies
COPY . .

# Set Flask environment variables
ENV FLASK_APP=web
ENV FLASK_ENV=development

# Expose Flask's default port
EXPOSE 5000

CMD ["poetry", "run", "flask", "run", "--host=0.0.0.0"]