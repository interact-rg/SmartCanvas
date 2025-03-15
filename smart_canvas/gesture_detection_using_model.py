from mediapipe.tasks import python
from mediapipe.tasks.python import vision, BaseOptions
import mediapipe as mp
import cv2
from cv2.typing import MatLike
# Types
from cv2.typing import MatLike
from typing import Protocol, Literal, Any

    
class GestureDetection:
    def __init__(self):
 

        
        # Setup the new GestureRecognizer model
        self.options = vision.GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_buffer=open("models/gesture_recognizer.task", "rb").read()),
            running_mode=vision.RunningMode.IMAGE,  
            num_hands=1
         )
        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)

    def detect_gestures(self, frame: MatLike):

        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 2) Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)


        result = self.recognizer.recognize(mp_image)

        if result.gestures:
            top_gesture = result.gestures[0][0].category_name
            print(f"Detected gesture: {top_gesture}")
            return top_gesture
        else:
            print("No hands detected.")
            return "No hands detected"
