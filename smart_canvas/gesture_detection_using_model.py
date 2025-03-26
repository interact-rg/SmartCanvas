import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision, BaseOptions
import mediapipe as mp
import cv2
from cv2.typing import MatLike
from typing import Protocol, Literal, Any

    
class GestureDetection:
    def __init__(self):
 

        
        # Setup the new GestureRecognizer model
        self.options = vision.GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_buffer=open("models/gesture_recognizer.task", "rb").read()),
            running_mode=vision.RunningMode.VIDEO,  
            num_hands=1
         )
        
        self.timestamp = time.time() * 1000

        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)

    def detect_gestures(self, frame: MatLike) -> tuple[str, tuple[float, float]]:
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 2) Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        new_timestamp = int(time.time() * 1000)
        if new_timestamp <= self.timestamp:
            new_timestamp = self.timestamp + 1
        self.timestamp = new_timestamp

        result = self.recognizer.recognize_for_video(mp_image, self.timestamp)
        

        if result.gestures:
            top_gesture = result.gestures[0][0].category_name
            wrist_location = (result.hand_landmarks[0][0].x, result.hand_landmarks[0][0].y)  
            print(f"Detected gesture: {top_gesture} with wrist at position: {wrist_location[0]}x {wrist_location[1]}y")
            return top_gesture, wrist_location
        else:
            print("No hands detected.")
            return "No hands detected", (0, 0)
