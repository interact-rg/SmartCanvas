FROM python:3.12-slim

ENV POETRY_HOME="/opt/poetry"
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

# Set working directory inside the container
WORKDIR /SmartCanvas

# Install system dependencies for Poetry & project
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg libsm6 libxext6 nodejs npm
	
# Install Poetry
RUN pip install poetry

# Copy only dependency files first (to leverage Docker cache)
COPY pyproject.toml poetry.lock ./

# Install dependencies before copying the full project
RUN poetry install --no-root --no-interaction --no-ansi

WORKDIR /SmartCanvas/smartcanvas-frontend
COPY smartcanvas-frontend/package.json smartcanvas-frontend/package-lock.json ./

RUN npm install

WORKDIR /SmartCanvas
COPY . .

ENV FLASK_APP=web
ENV FLASK_ENV=development
ENV FLASK_DEBUG=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000 5173

CMD ["sh", "-c", "cd smartcanvas-frontend && npm run dev -- --host & poetry run flask run --host=0.0.0.0 --debug"]
