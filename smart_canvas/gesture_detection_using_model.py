import time
from mediapipe.tasks.python import vision, BaseOptions
import mediapipe as mp
import cv2
from cv2.typing import MatLike
from typing import Tuple
from collections import deque

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
        self.previous_gesture = "No gesture detected"
        #self.swipe_timer = None
        self.current_fingertip_x = None
        self.previous_fingertip_x = None
        self.armed_fingertip_x = None
        self.stable_duration = 0.0
        self.hand_width = 0.0

        self.latest_gestures = deque(maxlen=30)


        self.movement_stable_start_time = None
        self.movement_stable_duration = 0.0
        

        self.gesture = "No gesture detected"
        self.wrist_location = (0.0, 0.0)
        self.swipe_armed = False
        self.swipe_arming_time = 0.0


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

        if not result.hand_landmarks:
             return None
        else:
            if result.gestures[0][0] and result.gestures[0][0].category_name:
                        self.gesture = result.gestures[0][0].category_name

            if self.stable_start_time is None:
                self.stable_start_time = time.time()
            elif self.gesture != self.previous_gesture:
                self.stable_start_time = time.time()
                self.previous_gesture = self.gesture
            else:
                self.stable_duration = time.time() - self.stable_start_time

            self.wrist_location = (result.hand_landmarks[0][0].x, result.hand_landmarks[0][0].y)
            self.previous_fingertip_x = self.current_fingertip_x
            self.current_fingertip_x = result.hand_landmarks[0][8].x



            x_coords = [lm.x for lm in result.hand_landmarks[0]]
            self.hand_width = max(x_coords) - min(x_coords)

            relative_threshold = 0.2 * self.hand_width
            if self.previous_fingertip_x is not None and abs(self.current_fingertip_x - self.previous_fingertip_x) > relative_threshold:
                self.movement_stable_start_time = time.time()
                self.movement_stable_duration = 0.0
                print("Finger movement detected above treshold...")
            else:
                if self.movement_stable_start_time is None:
                    self.movement_stable_start_time = time.time()
                    self.movement_stable_duration = 0.0
                else:   
                    self.movement_stable_duration = time.time() - self.movement_stable_start_time
    
            self.latest_gestures.append(self.gesture)

        return self.gesture, self.wrist_location, self.stable_duration

    def finger_swipe(self):
        
        swipe = None

        if self.swipe_armed and time.time() - self.swipe_arming_time > 3.0:
            print("Swipe timed out...")
            self.swipe_armed = False
            return None


        if "Swipe_Armed" in self.latest_gestures:
            if (self.swipe_armed == False) and self.movement_stable_duration >= 0.4:
                self.swipe_armed = True
                self.armed_fingertip_x = self.current_fingertip_x
                self.swipe_arming_time = time.time()

                print("Swipe has been armed...")
                return "Swipe_Armed"
        
        if self.swipe_armed == True:
            dynamic_threshold = self.hand_width * 0.5
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