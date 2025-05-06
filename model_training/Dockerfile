# syntax=docker/dockerfile:1.4  # enable BuildKit features

ARG TF_TAG=2.15.0
ARG TF_FLAVOR=gpu
FROM tensorflow/tensorflow:${TF_TAG}${TF_FLAVOR:+-${TF_FLAVOR}}

# system deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "training.py"]
