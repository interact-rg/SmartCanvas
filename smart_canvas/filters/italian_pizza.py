from smart_canvas.filters.base import Filter
from smart_canvas.face_detection import FaceDetection
from cv2.typing import MatLike
import cv2
import numpy as np

class ItalianPizza(Filter):
    background = 'italy_bg.jpeg'  # Italian landscape background
    italy_hat = 'italy_hat.png'   # Pizza chef hat or pizza slice overlay
    moustache = 'italian_moustache.png'  # Italian style moustache overlay
    
    def __init__(self):
        super().__init__()
        self.face_detector: FaceDetection = FaceDetection(running_mode='IMAGE')
        self.pizza_img = cv2.imread(self.bg_root + self.italy_hat, cv2.IMREAD_UNCHANGED)
        self.moustache_img = cv2.imread(self.bg_root + self.moustache, cv2.IMREAD_UNCHANGED)

    def filter(self, frame: MatLike) -> MatLike:
        # Create warm Italian sunlight effect
        # Increase red and yellow tones, slightly decrease blue
        
        # Convert to HSV for easier color manipulation
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Enhance saturation for vibrant Italian colors
        saturation_factor = 1.3
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * saturation_factor, 0, 255).astype(np.uint8)
        
        # Shift hue slightly toward yellow/orange (Italian warm light)
        # Hue values in OpenCV range from 0-179
        warm_shift = 5  # Slight shift toward warm tones
        hsv[:, :, 0] = np.clip(hsv[:, :, 0] - warm_shift, 0, 179).astype(np.uint8)
        
        # Increase brightness slightly
        brightness_factor = 1.1
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * brightness_factor, 0, 255).astype(np.uint8)
        
        # Convert back to BGR
        italian_result = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        
        # Optional: Add a slight vignette for that "postcard from Italy" feel
        height, width = frame.shape[:2]
        x_center = width // 2
        y_center = height // 2
        
        # Create radial mask for vignette
        mask = np.zeros((height, width), dtype=np.float32)
        for y in range(height):
            for x in range(width):
                # Calculate distance from center (normalized)
                distance = np.sqrt((x - x_center) ** 2 + (y - y_center) ** 2) / (np.sqrt(x_center ** 2 + y_center ** 2) * 1.2)
                # Inverse the distance and clip between 0.7 and 1.0
                mask[y, x] = np.clip(1.0 - distance, 0.8, 1.0)
        
        # Apply vignette
        for c in range(3):
            italian_result[:, :, c] = italian_result[:, :, c] * mask
        
        return italian_result
    
    def apply_overlay(self, image, overlay_img, x, y, width, height):
        """Helper function to apply an overlay with alpha blending"""
        overlay_resized = cv2.resize(overlay_img, (width, height), interpolation=cv2.INTER_AREA)
        
        # Make sure we stay within image boundaries
        y_start = max(0, y)
        y_end = min(image.shape[0], y + height)
        x_start = max(0, x)
        x_end = min(image.shape[1], x + width)
        
        # Adjust overlay image coordinates
        oy_start = max(0, -y)
        oy_end = height - max(0, (y + height) - image.shape[0])
        ox_start = max(0, -x)
        ox_end = width - max(0, (x + width) - image.shape[1])
        
        # Only proceed if we have valid regions
        if oy_end > oy_start and ox_end > ox_start:
            for c in range(0, 3):
                image[y_start:y_end, x_start:x_end, c] = \
                    (overlay_resized[oy_start:oy_end, ox_start:ox_end, 3] / 255.0 * 
                     overlay_resized[oy_start:oy_end, ox_start:ox_end, c] +
                    (1 - overlay_resized[oy_start:oy_end, ox_start:ox_end, 3] / 255.0) * 
                     image[y_start:y_end, x_start:x_end, c])
        
        return image
    
    def mask_background(self, frame: MatLike, background: MatLike, mask: MatLike) -> MatLike:
        image = super().mask_background(frame, background, mask)
        # Detect faces in the image
        detection_result = self.face_detector.detect_faces(frame)
        if detection_result:
            o_image = image.copy()
            try:
                for face in detection_result.detections:
                    bboxC = face.bounding_box
                    
                    # Get face landmarks if available
                    has_landmarks = hasattr(face, 'keypoints') and face.keypoints is not None
                    
                    # 1. Apply pizza chef hat
                    # Scale pizza image with increased size factor
                    pizza_width = int(bboxC.width * 2.0)  # Much larger than the face
                    pizza_height = int(pizza_width * self.pizza_img.shape[0] / self.pizza_img.shape[1])
                    
                    # Adjust position to place the pizza hat
                    left_shift = 27  # Shift to the left
                    pizza_x = int(bboxC.origin_x - (pizza_width - bboxC.width) / 2) - left_shift
                    pizza_y = int(bboxC.origin_y - (pizza_height * 0.90))  # Slightly higher position for bigger hat
                    
                    # Apply the hat overlay
                    image = self.apply_overlay(image, self.pizza_img, pizza_x, pizza_y, pizza_width, pizza_height)
                    
                    # 2. Apply moustache
                    # Calculate position for moustache based on face dimensions
                    # If we have landmarks, we could use them, but for now use face dimensions
                    moustache_width = int(bboxC.width * 0.8)  # Slightly narrower than face
                    moustache_height = int(moustache_width * self.moustache_img.shape[0] / self.moustache_img.shape[1])
                    
                    # Position the moustache at the lower third of the face (approximate mouth location)
                    moustache_x = int(bboxC.origin_x + (bboxC.width - moustache_width) / 2)
                    moustache_y = int(bboxC.origin_y + bboxC.height * 0.5)  # Positioned at approximately x% down the face
                    
                    # Apply the moustache overlay
                    image = self.apply_overlay(image, self.moustache_img, moustache_x, moustache_y, moustache_width, moustache_height)
                    
            except Exception as e:
                print(f"Error applying overlays: {e}")
                return o_image
        return image