import time
import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
from cv2.typing import MatLike
from typing import Optional, Tuple, List
from mediapipe.tasks.python.components.containers.landmark import NormalizedLandmark

class GestureDetection:


    GestureResult = Tuple[
        str,                    # detected gesture category
        Tuple[float, float],    # wrist (x, y)
        float,                  # how long it's been stable
        List[NormalizedLandmark]  # list of hand landmarks
    ]

    def __init__(self, model_path: str = "models/gesture_recognizer.task"):
        with open(model_path, "rb") as f:
            buffer = f.read()

        self.options = vision.GestureRecognizerOptions(
            base_options=BaseOptions(model_asset_buffer=buffer),
            running_mode=vision.RunningMode.VIDEO,
            num_hands=1,
        )
        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)

        self.timestamp = int(time.time() * 1000)
        self.previous_gesture: str = ""
        self.candidate_gesture: str = ""
        self.candidate_start_time: Optional[float] = None
        self.stable_start_time: Optional[float] = None
        self.stable_duration: float = 0.0
        self.switch_thresh = 0.1

    def detect_gestures(self, frame: MatLike) -> GestureResult | None:

        # Convert BGR to RGB
        try:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception:
            return None

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        result = self.recognizer.recognize_for_video(mp_image, self._next_timestamp())
        
        
        # No hand detected
        if not result.hand_landmarks:
            self.reset_state()
            return None
        # Grab first hand landmarks and gesture
        hand_lms = result.hand_landmarks[0]
        gestures = result.gestures or [[]]
        
        gesture_name = gestures[0][0].category_name if gestures[0] else "Unknown"

        if gesture_name == "Point_Finger" or gesture_name == "Point_Gun":
                direction = self.check_direction(hand_lms)
                gesture_name = gesture_name + direction
        
        now = time.time()

        if gesture_name != self.candidate_gesture:
            self.candidate_gesture = gesture_name
            self.candidate_start_time = now

        
        cand_dur = now - (self.candidate_start_time or now)

        # 3) only switch “previous_gesture” once candidate has been stable long enough
        if (self.candidate_gesture != self.previous_gesture
            and cand_dur >= self.switch_thresh):
            self.previous_gesture = self.candidate_gesture
            self.stable_start_time = self.candidate_start_time
            self.stable_duration = cand_dur

                
                
        # 4) if it’s still the same as previous, just update stable_duration
        elif self.candidate_gesture == self.previous_gesture:
            self.stable_duration = now - (self.stable_start_time or now)
        else:
            # candidate hasn’t yet “locked in” — keep stable_duration at zero  
            self.stable_duration = 0.0

        # Wrist coordinate is landmark 0
        wrist = (hand_lms[0].x, hand_lms[0].y)
        
     

        return self.previous_gesture, wrist, self.stable_duration, hand_lms

    def reset_state(self):
        """Wipe out *all* in‑flight gesture timing so we start fresh next time."""
        self.previous_gesture        = ""
        self.candidate_gesture       = ""
        self.candidate_start_time    = None
        self.stable_start_time       = None
        self.stable_duration         = 0.0

    def check_direction(
        self,
        hand_lms: List[NormalizedLandmark]
    ) -> str:

        # Type‑guard
        if not hand_lms or len(hand_lms) <= 8:
            return ""
        wrist_x = hand_lms[0].x
        tip_x   = hand_lms[8].x
    
        if tip_x > wrist_x: # type: ignore
            return "_Left"
        if tip_x < wrist_x: # type: ignore
            return "_Right"
        return ""
        
        



    def _next_timestamp(self) -> int:
        """Ensure strictly increasing timestamps for video frames."""
        new_ts = int(time.time() * 1000)
        if new_ts <= self.timestamp:
            new_ts = self.timestamp + 1
        self.timestamp = new_ts
        return new_ts