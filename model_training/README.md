IMPORTANT!

If you are developing on a Windows machine; it is recommended use the Dockerized version of the model training script. It is recommended to adapt 
the training script to your needs.

See https://ai.google.dev/edge/mediapipe/solutions/vision/gesture_recognizer for documentation.

For training on CPU, simply run:
docker compose up --build      

To use a GPU (NVIDIA) to speed up training, create an .env file with the following content:

# .env
TF_FLAVOR=gpu
DOCKER_RUNTIME=nvidia


******************************

The dataset folder includes a limited number of sample images for each gesture. If you re-train the model and find that it is not accurate enough, consider adding to the data.

Adjust the training parameters to suit your hardware and needs. After training, find the newly exported model in exported_model. 
To use it with Smart Canvas, replace gesture_recognizer.task in root/models with the new model.