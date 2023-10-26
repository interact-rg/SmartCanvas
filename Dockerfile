FROM python:3.11.5-bullseye AS builder

WORKDIR /smart-canvas

COPY setup.py README.md .

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install .

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
COPY . .

ENV FLASK_APP web
ENV CLIENT_TOKEN d159f6d5-6bb6-44c3-a2fa-ae5a60b5ce75

ENTRYPOINT ["python", "-m", "flask", "run", "--host=0.0.0.0"]
