FROM python:3.11.5-bullseye AS builder

WORKDIR /smart-canvas

COPY setup.py README.md ./

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY . .

ENV FLASK_APP=web
COPY .env .env
RUN export $(cat .env | xargs)

ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]

# ENTRYPOINT ["gunicorn", "-b", "0.0.0.0:5000", "--worker-class", "eventlet", "-w", "2", "web:create_app()"]
# To enable gunicorn (a WSGI server) uncomment the line above and comment the line WORKDIR