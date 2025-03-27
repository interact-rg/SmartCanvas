import os
import tensorflow as tf
assert tf.__version__.startswith('2')

# Check for GPU availability
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    print("GPU is available:", gpus)
else:
    print("GPU is not available. Running on CPU.")

from mediapipe_model_maker import gesture_recognizer
import matplotlib.pyplot as plt

# Define the local dataset directory (this should be mounted into the container)
DATASET_DIR = "dataset"
if not os.path.exists(DATASET_DIR):
    raise ValueError(f"Dataset directory '{DATASET_DIR}' does not exist. Please mount your dataset.")

# Optionally, list the labels (assumes subdirectories per label)
labels = [d for d in os.listdir(DATASET_DIR) if os.path.isdir(os.path.join(DATASET_DIR, d))]
print("Found labels:", labels)

# Load the dataset using the hand data preprocessing parameters
print("Loading dataset...")
data = gesture_recognizer.Dataset.from_folder(
    dirname=DATASET_DIR,
    hparams=gesture_recognizer.HandDataPreprocessingParams()
)
print("Dataset loaded successfully.")

# Split the dataset: 80% train, 10% validation, 10% test.
train_data, rest_data = data.split(0.8)
validation_data, test_data = rest_data.split(0.5)
print("Dataset split into training, validation, and test sets.")

# Set training hyperparameters (adjust batch_size, epochs, etc. as needed)
hparams = gesture_recognizer.HParams(
    export_dir="exported_model",  # This directory is mounted to your host to persist the model
    batch_size=4,
    epochs=5
)
options = gesture_recognizer.GestureRecognizerOptions(hparams=hparams)

# Train the gesture recognizer model
print("Starting model training...")
model = gesture_recognizer.GestureRecognizer.create(
    train_data=train_data,
    validation_data=validation_data,
    options=options
)
print("Model training complete.")

# Evaluate the trained model on the test set
print("Evaluating model...")
loss, accuracy = model.evaluate(test_data, batch_size=1)
print(f"Test Loss: {loss}, Test Accuracy: {accuracy}")

# Export the model to TFLite format (includes model metadata)
print("Exporting model...")
model.export_model()
print("Model exported successfully. Exported files:")
print(os.listdir("exported_model"))