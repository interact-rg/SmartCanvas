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
            min_hand_detection_confidence=0.3,  # Default is 0.5
            min_hand_presence_confidence=0.3,   # Default is 0.5
            min_tracking_confidence=0.3  # Default is 0.5
            
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
        
        self.rescale_factor = 1.5


        self.gesture = "No gesture detected"
        self.wrist_location = (0.0, 0.0)
        self.swipe_armed = False
        self.swipe_arming_time = 0.0


        self.position_history = deque(maxlen=5)  # Store last 5 positions
        self.gesture_history = deque(maxlen=3)   # Store last 3 gestures




    GestureResult = Tuple[str, Tuple[float, float], float]

    def detect_gestures(self, frame: MatLike) -> GestureResult|None:
        # Convert BGR to RGB

        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print("Error during frame preparation (gesture detection)")
            return "No hands detected", (0.0, 0.0), 0.0


        # Upscale to help detect small hands
        h, w = frame_rgb.shape[:2]
        frame_rgb = cv2.resize(
            frame_rgb,
            (int(w * self.rescale_factor), int(h * self.rescale_factor)),
            interpolation=cv2.INTER_CUBIC,
        )


        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)

        # Ensure new timestamp is always greater than the previous one

        self.timestamp = self.generate_timestamp()

        result = self.recognizer.recognize_for_video(mp_image, self.timestamp)

        if not result.hand_landmarks:
             self.stable_duration = 0.0
             self.stable_start_time = None
             return None
        else:
            # Store wrist position in history
            current_wrist = (result.hand_landmarks[0][0].x, result.hand_landmarks[0][0].y)
            self.position_history.append(current_wrist)
            
            # Average the positions for stability
            if len(self.position_history) > 0:
                avg_x = sum(pos[0] for pos in self.position_history) / len(self.position_history)
                avg_y = sum(pos[1] for pos in self.position_history) / len(self.position_history)
                self.wrist_location = (avg_x, avg_y)
            else:
                self.wrist_location = current_wrist
                
            # Use gesture voting for stability
            if result.gestures[0][0] and result.gestures[0][0].category_name:
                current_gesture = result.gestures[0][0].category_name
                self.gesture_history.append(current_gesture)
                
                # Use most common gesture from history
                if len(self.gesture_history) > 0:
                    from collections import Counter
                    gesture_counts = Counter(self.gesture_history)
                    most_common_gesture = gesture_counts.most_common(1)[0][0]
                    
                    if self.gesture != most_common_gesture:
                        self.previous_gesture = self.gesture
                        self.gesture = most_common_gesture
                        self.set_hand_width(result)
                        self.swipe_armed = False

            if self.stable_start_time is None:
                self.stable_start_time = time.time()
            elif self.gesture != self.previous_gesture:
                self.set_hand_width(result)
                self.stable_start_time = time.time()
                self.previous_gesture = self.gesture
            else:
                self.stable_duration = time.time() - self.stable_start_time

            self.wrist_location = (result.hand_landmarks[0][0].x, result.hand_landmarks[0][0].y)
            self.previous_fingertip_x = self.current_fingertip_x
            self.current_fingertip_x = result.hand_landmarks[0][8].x


            relative_threshold = 0.4 * self.hand_width
            if self.previous_fingertip_x is not None and abs(self.current_fingertip_x - self.previous_fingertip_x) > relative_threshold:
                self.movement_stable_start_time = time.time()
                self.movement_stable_duration = 0.0
                if self.swipe_armed == False:
                    print("Finger movement detected above treshold...")
            else:
                if self.movement_stable_start_time is None:
                    self.movement_stable_start_time = time.time()
                    self.movement_stable_duration = 0.0
                else:   
                    self.movement_stable_duration = time.time() - self.movement_stable_start_time
    

        return self.gesture, self.wrist_location, self.stable_duration

    def finger_swipe(self) -> str|None:
        # Check if swipe is armed and if the swipe timer has expired          
        # If swipe is armed, check if the finger has moved a certain distance
        # If so, return the swipe direction
        
        swipe = None
        
        if (self.swipe_armed and time.time() - self.swipe_arming_time > 5.0):
            print("Swipe timed out...")
            self.swipe_armed = False
            return None 

        if self.gesture == "Swipe_Armed":
            if (self.swipe_armed == False) and self.movement_stable_duration >= 0.3:
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
        

    def set_hand_width(self, result):
        x_coords = [lm.x for lm in result.hand_landmarks[0]]
        self.hand_width = max(x_coords) - min(x_coords)

    def generate_timestamp(self) -> int:
        new_timestamp = int(time.time() * 1000)
        if new_timestamp <= self.timestamp:
           new_timestamp = self.timestamp + 1
        return new_timestamp