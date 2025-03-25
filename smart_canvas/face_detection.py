import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
from cv2.typing import MatLike
import cv2
    
class FaceDetection:

    def __init__(self):

        
        base_options = python.BaseOptions(model_asset_path='models/blaze_face_short_range.tflite')
        options = vision.FaceDetectorOptions(base_options=base_options)
        self.detector = vision.FaceDetector.create_from_options(options)

        if self.detector is None:
            raise RuntimeError("Failed to load face detection model from" + base_options.model_asset_path)
        else: print("Face detection model loaded from" + base_options.model_asset_path)

        self.stable_time = None
        self.unstable_start_time = None



    def detect_face(self, frame: MatLike) -> tuple[bool, float]:
        
        # Convert BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #convert to mediapipe image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        detection_result = self.detector.detect(mp_image)

        face_present = bool(detection_result and detection_result.detections)
        current_time = time.time()

        if face_present:
            # If this is the first frame in which a face appears, record the time
            if self.stable_time is None:
                self.unstable_start_time = None
                self.stable_time = current_time
            stable_for = (current_time - self.stable_time)
            return face_present, stable_for
        else:
            self.stable_time = None
            if self.unstable_start_time is None:
                self.unstable_start_time = current_time
            unstable_for = current_time - self.unstable_start_time
            return face_present, unstable_for
