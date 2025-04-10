import os
import datetime
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

# Split the dataset: 70% for training, 15% for validation, and 15% for testing.  Increased validation and test set size.
train_data, rest_data = data.split(0.7)
validation_data, test_data = rest_data.split(0.5)

# Create a timestamp-based subfolder inside the mapped /app/exported_model directory.
timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
export_subfolder = f"model_{timestamp}"  # e.g. "model_2025-03-29_14-12-05"
export_dir = os.path.join("/app/exported_model", export_subfolder)
os.makedirs(export_dir, exist_ok=True)

# Create a model with customized hyperparameters
hparams = gesture_recognizer.HParams(
    export_dir=export_dir,
    epochs=40,  # Increased epochs
    batch_size=32, # Increased batch size
    learning_rate=0.0005,  # Adjusted learning rate
    lr_decay=0.995, # Adjusted learning rate decay
    shuffle=True,  # Enable shuffling
    gamma=2.0 # Added gamma for focal loss
)
options = gesture_recognizer.GestureRecognizerOptions(
    hparams=hparams,
    model_options=gesture_recognizer.ModelOptions(dropout_rate=0.3, layer_widths=[256, 128, 64]) # Added dropout and layers
)
model = gesture_recognizer.GestureRecognizer.create(
    train_data=train_data,
    validation_data=validation_data,
    options=options
)

# Implement early stopping
es_callback = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True) # added early stopping

print(f"Exporting model to: {export_dir}")
model.export_model()
print(f"Export finished. Check {export_dir} inside the container or './exported_model/{export_subfolder}' on your host.")



loss, acc = model.evaluate(test_data, batch_size=1)
print(f"Test loss:{loss}, Test accuracy:{acc}")