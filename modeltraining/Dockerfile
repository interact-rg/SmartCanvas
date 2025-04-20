# Dockerfile
ARG TF_TAG=2.15.0       # default version
ARG TF_FLAVOR=gpu       # "gpu" or ""  (empty → CPU)
FROM tensorflow/tensorflow:${TF_TAG}${TF_FLAVOR:+-${TF_FLAVOR}}

# deps & code exactly as you already have …
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "training.py"]