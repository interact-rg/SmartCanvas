import mediapipe as mp
import cv2
import numpy as np
import os

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)

def extract_landmarks_from_video(video_path, seq_length=20):
    cap = cv2.VideoCapture(video_path)
    landmarks_seq = []

    while len(landmarks_seq) < seq_length:
        success, frame = cap.read()
        if not success:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            landmarks = []
            for lm in results.multi_hand_landmarks[0].landmark:
                landmarks.extend([lm.x, lm.y, lm.z])
            landmarks_seq.append(landmarks)

    cap.release()
    # Pad sequences shorter than seq_length
    while len(landmarks_seq) < seq_length:
        landmarks_seq.append(np.zeros(21 * 3))
    return np.array(landmarks_seq)

dataset_video_path = "dataset/"
output_data, output_labels = [], []

labels_dict = {"swipe_left":0, "swipe_right":1}

for gesture in ["swipe_left", "swipe_right"]:
    class_path = os.path.join(dataset_video_path, gesture)
    for video_file in os.listdir(class_path):
        video_path = os.path.join(class_path, video_file)
        landmarks_seq = extract_landmarks_from_video(video_path)
        output_data.append(landmarks_seq)
        output_labels.append(labels_dict[gesture])

output_data = np.array(output_data)
output_labels = np.array(output_labels)

np.savez("gesture_landmarks_dataset.npz", data=output_data, labels=output_labels)
print("Landmark extraction completed.")