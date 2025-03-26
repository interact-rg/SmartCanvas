import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision, BaseOptions
import mediapipe as mp
import cv2
from cv2.typing import MatLike
from typing import Protocol, Literal, Any, NamedTuple, Tuple

class GestureDetection:
    def __init__(self):
        # Setup the new GestureRecognizer model
        self.options = vision.GestureRecognizerOptions(
        base_options=BaseOptions(model_asset_buffer=open("models/gesture_recognizer.task", "rb").read()),
        running_mode=vision.RunningMode.VIDEO,
        num_hands=1,
        )


        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)

        self.timestamp = int(time.time() * 1000)

        # Initialize stable duration, i.e. the time for which a gesture has been stable
        self.stable_start_time = None
        self.previous_gesture = "Unrecognized gesture"

    GestureResult = Tuple[str, Tuple[float, float], float]

    def detect_gestures(self, frame: MatLike) -> GestureResult:
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Ensure new timestamp is always greater than the previous one
        new_timestamp = int(time.time() * 1000)
        if new_timestamp <= self.timestamp:
            new_timestamp = self.timestamp + 1
        self.timestamp = new_timestamp

        result = self.recognizer.recognize_for_video(mp_image, self.timestamp)

        if result.gestures:
            

            top_gesture = result.gestures[0][0].category_name
            wrist_location = (result.hand_landmarks[0][0].x, result.hand_landmarks[0][0].y)

            if self.stable_start_time is None:
                self.stable_start_time = time.time()
            elif top_gesture != self.previous_gesture:
                # Reset stable start time for new gesture
                self.stable_start_time = time.time()
                self.previous_gesture = top_gesture
            else:
                stable_duration = time.time() - self.stable_start_time
                return top_gesture, wrist_location, stable_duration

            return top_gesture, wrist_location, 0.0
        else:
            return "No hands detected", [0.0, 0.0], 0.0