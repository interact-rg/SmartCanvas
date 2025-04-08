import os
import datetime
import glob
import tensorflow as tf
from PIL import Image


from mediapipe_model_maker import gesture_recognizer

print("code is running..")
# Check for GPU
if tf.config.list_physical_devices('GPU'):
    print("GPU detected.")
else:
    print("No GPU detected. Training on CPU.")

dataset_path = "/app/dataset"

print(dataset_path)
labels = []
for i in os.listdir(dataset_path):
  if os.path.isdir(os.path.join(dataset_path, i)):
    labels.append(i)
print(labels)

# Load the dataset from the folder
data = gesture_recognizer.Dataset.from_folder(
    dirname=dataset_path,
    hparams=gesture_recognizer.HandDataPreprocessingParams()
)

# Split the dataset: 80% for training, 10% for validation, and 10% for testing.
train_data, rest_data = data.split(0.8)
validation_data, test_data = rest_data.split(0.5)

# Create a timestamp-based subfolder inside the mapped /app/exported_model directory.
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
export_subfolder = f"model_{timestamp}"  # e.g. "model_2025-03-29_14-12-05"
export_dir = os.path.join("/app/exported_model", export_subfolder)
os.makedirs(export_dir, exist_ok=True)

# Create a model with the default hyperparameters
hparams = gesture_recognizer.HParams(export_dir=export_dir, epochs=20, batch_size=16)
options = gesture_recognizer.GestureRecognizerOptions(hparams=hparams)
model = gesture_recognizer.GestureRecognizer.create(
    train_data=train_data,
    validation_data=validation_data,
    options=options
)



print(f"Exporting model to: {export_dir}")
model.export_model()
print(f"Export finished. Check {export_dir} inside the container or './exported_model/{export_subfolder}' on your host.")



loss, acc = model.evaluate(test_data, batch_size=1)
print(f"Test loss:{loss}, Test accuracy:{acc}")

