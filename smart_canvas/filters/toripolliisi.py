from smart_canvas.filters.base import Filter
from smart_canvas.face_detection import FaceDetection
from cv2.typing import MatLike
import cv2
import numpy as np

class Toripolliisi(Filter):
    background = 'tori_bg.jpeg'
    hat = 'toripolliisi_hat.png'

    def __init__(self):
        super().__init__()
        self.face_detector: FaceDetection = FaceDetection(running_mode='IMAGE')
        self.hat_img = cv2.imread(self.bg_root + self.hat, cv2.IMREAD_UNCHANGED)


    def filter(self, frame: MatLike) -> MatLike:
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


        # Enhance local contrast
        clahe = cv2.createCLAHE(clipLimit=4.0, tileGridSize=(8, 8))
        enhanced_gray = clahe.apply(gray)

        # Define gradient endpoints for bronze color
        dark = np.array([25, 28, 30], dtype=np.uint8)
        light = np.array([113, 123, 118], dtype=np.uint8)

        # Create LUT for color gradient
        lut = np.zeros((256, 1, 3), dtype=np.uint8)
        for i in range(256):
            # Linearly interpolate between dark and light bronze based on intensity i
            interp_factor = i / 255.0
            color = dark * (1 - interp_factor) + light * interp_factor
            lut[i, 0, :] = color.astype(np.uint8) # Ensure uint8 type

        gray_3channel = cv2.cvtColor(enhanced_gray, cv2.COLOR_GRAY2BGR)
        # Apply LUT
        bronze_result = cv2.LUT(gray_3channel, lut)

        return bronze_result
    
    def mask_background(self, frame: MatLike, background: MatLike, mask: MatLike) -> MatLike:
        image = super().mask_background(frame, background, mask)
        # Detect faces in the image
        detection_result = self.face_detector.detect_faces(frame)
        if detection_result:
            o_image = image.copy()
            # TODO: Test if the alpha overlay can out of bounds error
            try:
                for face in detection_result.detections:
                    bboxC = face.bounding_box
                    top_left = (int(bboxC.origin_x), int(bboxC.origin_y))
                    top_right = (int(bboxC.origin_x + bboxC.width), int(bboxC.origin_y))

                    # Scale hat image to fit width to bounding box width
                    hat_width = int(bboxC.width * 1.3)
                    hat_height = int(hat_width * self.hat_img.shape[0] / self.hat_img.shape[1])

                    hat_resized = cv2.resize(self.hat_img, (hat_width, hat_height), interpolation=cv2.INTER_AREA)

                    # Calculate position to place the hat
                    hat_x = int(bboxC.origin_x - (hat_width - bboxC.width) / 2)
                    hat_y = int(bboxC.origin_y - (hat_height * 0.75))

                    # Alpha overlay the hat on the image
                    for c in range(0, 3):
                        image[hat_y:hat_y + hat_height, hat_x:hat_x + hat_width, c] = \
                            (hat_resized[:, :, 3] / 255.0 * hat_resized[:, :, c] +
                            (1 - hat_resized[:, :, 3] / 255.0) * image[hat_y:hat_y + hat_height, hat_x:hat_x + hat_width, c])
            except Exception as e:
                print(f"Error applying hat: {e}")
                return o_image
        return image


    

