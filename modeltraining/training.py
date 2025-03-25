import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

data = np.load("gesture_landmarks_dataset.npz")['data']
labels = np.load("gesture_landmarks_dataset.npz")['labels']

X_train, X_test, y_train, y_test = train_test_split(data, labels, test_size=0.2, random_state=42)

y_train_cat = to_categorical(y_train)
y_test_cat = to_categorical(y_test)

model = Sequential([
    LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2]), return_sequences=False),
    Dense(32, activation='relu'),
    Dense(2, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(X_train, y_train_cat, epochs=20, batch_size=8, validation_split=0.2)

loss, acc = model.evaluate(X_test, y_test_cat)
print(f"Accuracy: {acc:.4f}")

model.save("gesture_landmark_model.h5")