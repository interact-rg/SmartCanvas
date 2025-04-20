For training on CPU, simply run:
docker compose up --build      

To use a GPU (NVIDIA):

docker compose -f docker-compose.yml -f docker-compose.gpu.yml up --build

