import time
from mediapipe.tasks.python import vision, BaseOptions
import mediapipe as mp
import cv2
from cv2.typing import MatLike
from typing import List, Tuple
from collections import deque
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark # <-- Import NormalizedLandmark


class GestureDetection:
    def __init__(self):
        # Setup the new GestureRecognizer model
        self.options = vision.GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_buffer=open("models/gesture_recognizer.task", "rb").read()),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.1,  # Default is 0.5
            min_hand_presence_confidence=0.1,   # Default is 0.5
            min_tracking_confidence=0.1  # Default is 0.5
        )

        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)

        self.timestamp = int(time.time() * 1000)

        # Initialize stable duration, i.e. the time for which a gesture has been stable
        self.stable_start_time = None
        self.previous_gesture = "No gesture detected"
        self.current_fingertip_x = None
        self.previous_fingertip_x = None
        self.armed_fingertip_x = None
        self.stable_duration = 0.0
        self.hand_width = 0.0

        self.movement_stable_start_time = None
        self.movement_stable_duration = 0.0
        

        self.gesture = "No gesture detected"
        self.wrist_location = (0.0, 0.0)
        self.swipe_armed = False
        self.swipe_arming_time = 0.0




    GestureResult = Tuple[str, Tuple[float, float], float, List[NormalizedLandmark]] # <-- Added List[...]

    def detect_gestures(self, frame: MatLike) -> GestureResult|None:
        # Convert BGR to RGB

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print("Error during frame preparation (gesture detection)")
            return None

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Ensure new timestamp is always greater than the previous one

        self.timestamp = self.generate_timestamp()

        result = self.recognizer.recognize_for_video(mp_image, self.timestamp)

        landmarks = result.hand_landmarks
        if not landmarks:
            # no hands: reset stable timers but keep gesture state
            self.stable_duration = 0.0
            self.stable_start_time = None
            return None



    

        # alias for clarity
        hand_lms = landmarks[0]
        hand_gs = result.gestures[0] if result.gestures else None



        if hand_gs and hand_gs[0].category_name:
            if self.gesture != hand_gs[0].category_name:
                self.previous_gesture = self.gesture
                self.gesture = hand_gs[0].category_name
                self.set_hand_width(result, 0)
                self.swipe_armed = False

        if self.stable_start_time is None:
            self.stable_start_time = time.time()
        elif self.gesture != self.previous_gesture:
            self.set_hand_width(result)
            self.stable_start_time = time.time()
            self.previous_gesture = self.gesture
        else:
            self.stable_duration = time.time() - self.stable_start_time

        self.wrist_location = (hand_lms[0].x, hand_lms[0].y)
        self.previous_fingertip_x = self.current_fingertip_x
        self.current_fingertip_x = hand_lms[8].x

        relative_threshold = 0.4 * self.hand_width
        if (self.previous_fingertip_x is not None and
            abs(self.current_fingertip_x - self.previous_fingertip_x) > relative_threshold):
            self.movement_stable_start_time = time.time()
            self.movement_stable_duration = 0.0
            if not self.swipe_armed:
                print("Finger movement detected above threshold...")
        else:
            if self.movement_stable_start_time is None:
                self.movement_stable_start_time = time.time()
                self.movement_stable_duration = 0.0
            else:
                self.movement_stable_duration = time.time() - self.movement_stable_start_time

        fingertip_position = (hand_lms[8].x, hand_lms[8].y)

        return self.gesture, self.wrist_location, self.stable_duration, fingertip_position
    
    def finger_swipe(self) -> str|None:
        # Check if swipe is armed and if the swipe timer has expired          
        # If swipe is armed, check if the finger has moved a certain distance
        # If so, return the swipe direction
        
        swipe = None
        
        if (self.swipe_armed and time.time() - self.swipe_arming_time > 2.0):
            print("Swipe timed out...")
            self.swipe_armed = False
            return None 

        if self.gesture == "Swipe_Armed":
            if (self.swipe_armed == False) and self.movement_stable_duration >= 0.4:
                self.swipe_armed = True
                self.armed_fingertip_x = self.current_fingertip_x
                self.swipe_arming_time = time.time()
            
                print("Swipe has been armed...")
                return "Swipe_Armed"
        
        if self.swipe_armed == True and self.current_fingertip_x is not None and self.armed_fingertip_x is not None:
            dynamic_threshold = self.hand_width * 1
            net_movement = self.current_fingertip_x - self.armed_fingertip_x

            if net_movement < -dynamic_threshold:
 
                        print("Swiping right...")
                        swipe = "Swipe_Right"
                        self.swipe_armed = False
                        self.swipe_arming_time = time.time()
            elif net_movement > dynamic_threshold:
                        print("Swiping left...")
                        swipe = "Swipe_Left"
                        self.swipe_armed = False
                        self.swipe_arming_time = time.time()
            return swipe
        

    def set_hand_width(self, result, idx: int = 0):
        # now takes an index argument
        xs = [lm.x for lm in result.hand_landmarks[idx]]
        self.hand_width = max(xs) - min(xs)

    def generate_timestamp(self) -> int:
        new_timestamp = int(time.time() * 1000)
        if new_timestamp <= self.timestamp:
           new_timestamp = self.timestamp + 1
        return new_timestamp
    
    def reset_state(self):
        """Reset all gesture‐detector state to initial values."""
        # timing & stability
        self.stable_start_time = None
        self.stable_duration = 0.0
        self.movement_stable_start_time = None
        self.movement_stable_duration = 0.0

        # gesture tracking
        self.previous_gesture = "No gesture detected"
        self.gesture = "No gesture detected"

        # fingertip positions
        self.current_fingertip_x = None
        self.previous_fingertip_x = None
        self.armed_fingertip_x = None

        # swipe state
        self.swipe_armed = False
        self.swipe_arming_time = 0.0

        # hand geometry
        self.hand_width = 0.0
        self.wrist_location = (0.0, 0.0)

        # ensure timestamp moves forward
        self.timestamp = int(time.time() * 1000)

