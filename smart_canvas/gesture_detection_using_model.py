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
        self.previous_fingertip_x = None
        self.swipe_timer = None
        self.current_fingertip_x = None

    GestureResult = Tuple[str, Tuple[float, float], float]

    def detect_gestures(self, frame: MatLike) -> GestureResult:
        # Convert BGR to RGB

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print("Error during frame preparation (gesture detection)")
            return "No hands detected", [0.0, 0.0], 0.0

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
            self.current_fingertip_x = result.hand_landmarks[0][8].x

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

    def finger_swipe(self):
        movement_threshold = 0.05  # Modify this to change the sensitivity of the detection

        swipe = None
        if self.swipe_timer is None:
            self.swipe_timer = time.time()
        if  (time.time() - self.swipe_timer > 1.5):
            if self.previous_fingertip_x is not None:

                if self.previous_fingertip_x - self.current_fingertip_x > movement_threshold:
                    print("Swiping right...")
                    swipe = "Swipe_Right"
                    self.swipe_timer = None

                elif self.current_fingertip_x - self.previous_fingertip_x > movement_threshold:
                    print("Swiping left...")
                    swipe = "Swipe_Left"
                    self.swipe_timer = None

        self.previous_fingertip_x = self.current_fingertip_x
        return swipe
