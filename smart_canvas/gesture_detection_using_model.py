import collections
from os import wait
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
        self.swipe_timer = None
        self.current_fingertip_x = None
        self.stable_duration = 0.0
        self.gesture = "No gesture detected"
        self.wrist_location = (0.0, 0.0)
        self.buffer_size = 5  # Number of frames to buffer
        self.fingertip_buffer = collections.deque(maxlen=self.buffer_size)

        self.swipe_right_cooldown = 0.0
        self.swipe_left_cooldown = 0.0


    GestureResult = Tuple[str, Tuple[float, float], float]

    def detect_gestures(self, frame: MatLike) -> GestureResult:
        # Convert BGR to RGB

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print("Error during frame preparation (gesture detection)")
            return "No hands detected", (0.0, 0.0), 0.0

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Ensure new timestamp is always greater than the previous one
        new_timestamp = int(time.time() * 1000)
        if new_timestamp <= self.timestamp:
            new_timestamp = self.timestamp + 1
        self.timestamp = new_timestamp

        result = self.recognizer.recognize_for_video(mp_image, self.timestamp)

        if result.gestures:

            self.gesture = result.gestures[0][0].category_name
            if self.stable_start_time is None:
                self.stable_start_time = time.time()
            elif self.gesture != self.previous_gesture:
                # Reset stable start time for new gesture
                self.stable_start_time = time.time()
                self.previous_gesture = self.gesture
            else:
                self.stable_duration = time.time() - self.stable_start_time

        else:
            # No recognized gesture
            self.gesture = "No gesture detected"

        if result.hand_landmarks:
            # Get the coordinates of the wrist and fingertip landmarks
            self.current_fingertip_x = result.hand_landmarks[0][8].x
            self.wrist_location = (result.hand_landmarks[0][0].x, result.hand_landmarks[0][0].y)
            self.fingertip_buffer.append(self.current_fingertip_x)

        else:
            self.current_fingertip_x = None
            self.wrist_location = (0.0, 0.0)
            self.stable_start_time = None
            self.stable_duration = 0.0
            

        return self.gesture, self.wrist_location, self.stable_duration

    def finger_swipe(self):
        movement_threshold = 0.2 # Modify this to change the sensitivity of the detection
        swipe = None
        base_cooldown = 0.3 # seconds
        if self.swipe_timer is None:
            self.swipe_timer = time.time()

        if len(self.fingertip_buffer) >= 2:
            oldest_x = self.fingertip_buffer[0]
            newest_x = self.fingertip_buffer[-1]
            net_movement = newest_x - oldest_x

        # Swipe Right
            if net_movement < -movement_threshold:
                if time.time() - self.swipe_timer >= base_cooldown + self.swipe_right_cooldown :
                    self.swipe_right_cooldown = 0.0
                    self.swipe_left_cooldown = 0.5
                    print("Swiping right...")
                    swipe = "Swipe_Right"
                    self.fingertip_buffer.clear()
                    self.swipe_timer = None

        # Swipe Left
            elif net_movement > movement_threshold:
                if time.time() - self.swipe_timer >= base_cooldown + self.swipe_left_cooldown:
                    self.swipe_left_cooldown = 0.0
                    self.swipe_right_cooldown = 0.5
                    print("Swiping left...")
                    swipe = "Swipe_Left"
                    self.fingertip_buffer.clear()
                    self.swipe_timer = None

        return swipe