import time
from mediapipe.tasks.python import vision, BaseOptions
from mediapipe.tasks.python.components.containers.detections import DetectionResult
from mediapipe.tasks.python.vision.face_detector import FaceDetector
from mediapipe.tasks.python.vision.core.vision_task_running_mode import VisionTaskRunningMode
import mediapipe as mp
from cv2.typing import MatLike
import cv2
from typing import Literal

class FaceDetection:
    _instance: "None|FaceDetection" = None

    def __new__(cls, running_mode: Literal['VIDEO', 'IMAGE'] = 'VIDEO'):
        if running_mode == 'IMAGE':
            if cls._instance is None:
                cls._instance = super(FaceDetection, cls).__new__(cls)
            return cls._instance
        else:
            return super(FaceDetection, cls).__new__(cls)
        
    def __init__(self, running_mode: Literal['VIDEO', 'IMAGE'] = 'VIDEO'):
        # Early return if already initialized (singleton)
        if hasattr(self, 'detector'):
            return
        
        if running_mode == 'VIDEO':
            self.running_mode = vision.RunningMode.VIDEO
        elif running_mode == 'IMAGE':
            self.running_mode = vision.RunningMode.IMAGE

        asset_path = "models/blaze_face_short_range.tflite"
        self.options = vision.FaceDetectorOptions(
            base_options=BaseOptions(model_asset_buffer=open(asset_path, "rb").read()),
            running_mode=self.running_mode,
        )
        self.detector: FaceDetector = vision.FaceDetector.create_from_options(self.options)

        if self.detector is None:
            raise RuntimeError("Failed to load face detection model from" + vision.FaceDetectorOptions.base_options.model_asset_path)
        
        self.stable_start_time = None
        self.unstable_start_time = None

        self.timestamp = int(time.time() * 1000)

    def detect_faces(self, frame: MatLike) -> DetectionResult|None:
        # Convert BGR to RGB
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb) # type: ignore
        except Exception as e:
            print("Error during frame preparation (face detection)")
            return None
        
        if self.running_mode == vision.RunningMode.VIDEO:
            #ensures new timestamp is always greater than the previous one
            new_timestamp = int(time.time() * 1000)
            if new_timestamp <= self.timestamp:
                new_timestamp = self.timestamp + 1
            self.timestamp = new_timestamp
            detection_result: DetectionResult = self.detector.detect_for_video(mp_image, self.timestamp)
        else:
            detection_result: DetectionResult = self.detector.detect(mp_image)


        if detection_result and detection_result.detections:
            return detection_result
        else:
            return None


    def detect_face_duration(self, frame: MatLike) -> tuple[bool, float]:
        current_time = time.time()

        face_present = bool(self.detect_faces(frame))

        if face_present:
            # If this is the first frame in which a face appears, start stable timer
            if self.stable_start_time is None:
                self.unstable_start_time = None
                self.stable_start_time = current_time

            # Calculate time for which face has been stable    
            stable_for = (current_time - self.stable_start_time)
            return face_present, stable_for
        else:
            self.stable_start_time = None
            if self.unstable_start_time is None:
                self.unstable_start_time = current_time
            unstable_for = current_time - self.unstable_start_time
            return face_present, unstable_for
