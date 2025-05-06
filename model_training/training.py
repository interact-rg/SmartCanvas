import os, datetime, tensorflow as tf
from mediapipe_model_maker import gesture_recognizer

print("Training on:", "GPU" if tf.config.list_physical_devices('GPU') else "CPU")

dataset_path = "/app/dataset"
print("Dataset path:", dataset_path)



# 1) Load & (optionally) shuffle
data = gesture_recognizer.Dataset.from_folder(
    dirname=dataset_path,
    hparams=gesture_recognizer.HandDataPreprocessingParams()
)
# 2) Split into train / val / test
train_data, rest_data       = data.split(0.7)
validation_data, test_data = rest_data.split(0.5)

timestamp    = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
export_sub   = f"model_{timestamp}"
export_dir   = os.path.join("/app/exported_model", export_sub)
os.makedirs(export_dir, exist_ok=True)
print("Exporting model to:", export_dir)


# 5) HParams & options (dropout/layers if desired)
hparams = gesture_recognizer.HParams(
     export_dir   = export_dir,
     epochs       = 40,        # up from 20
     batch_size   = 16,
     learning_rate = 5e-4,
     lr_decay     = 0.995,     # gentler decay
     shuffle      = True
 )

model_opts = gesture_recognizer.ModelOptions(
  dropout_rate=0.15,
  layer_widths=[512,256,128]   # a four‑layer head
)
options = gesture_recognizer.GestureRecognizerOptions(
    hparams=hparams,
    model_options=model_opts
)

# 6) Train!
model = gesture_recognizer.GestureRecognizer.create(
    train_data      = train_data,
    validation_data = validation_data,
    options         = options
)

# 7) Export & evaluate
model.export_model()
loss, acc = model.evaluate(test_data, batch_size=16)
print(f"Test loss: {loss:.4f} | Test accuracy: {acc:.2%}")
