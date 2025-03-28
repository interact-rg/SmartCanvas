import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import mediapipe as mp
from cv2.typing import MatLike
import cv2
    
class FaceDetection:

    def __init__(self):


        self.options = vision.FaceDetectorOptions(
            base_options=python.BaseOptions(model_asset_path='models/blaze_face_short_range.tflite'),
            running_mode=vision.RunningMode.VIDEO,  
         )
        self.detector = vision.FaceDetector.create_from_options(self.options)


        if self.detector is None:
            raise RuntimeError("Failed to load face detection model from" + vision.FaceDetectorOptions.base_options.model_asset_path)
        
        self.stable_start_time = None
        self.unstable_start_time = None

        self.timestamp = time.time() * 1000


    def detect_face(self, frame: MatLike) -> tuple[bool, float]:

        current_time = time.time()
        # Convert BGR to RGB
        try:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        except Exception as e:
            print("Error during frame preparation (face detection)")
            self.stable_start_time = None
            self.unstable_start_time = current_time
            unstable_for = current_time - self.unstable_start_time
            return False, unstable_for 

        #convert to mediapipe image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        
        #ensures new timestamp is always greater than the previous one
        new_timestamp = int(time.time() * 1000)
        if new_timestamp <= self.timestamp:
            new_timestamp = self.timestamp + 1
        self.timestamp = new_timestamp

        detection_result = self.detector.detect_for_video(mp_image, self.timestamp)

        face_present = bool(detection_result and detection_result.detections)

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
