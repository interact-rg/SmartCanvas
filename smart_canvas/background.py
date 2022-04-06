import cv2
import numpy as np
import mediapipe as mp
mp_selfie_segmentation = mp.solutions.selfie_segmentation

class ForegroundMask:
    """
    Class that gives the foreground mask.
    """

    def __init__(self):
        self.selfie_segmentation = mp_selfie_segmentation.SelfieSegmentation(model_selection=1)
        self.bg_image = cv2.imread('smart_canvas/backgrounds/IMG_2792.jpg')
        dim = (1280,720)
        self.bg_image = cv2.resize(self.bg_image, dim, interpolation = cv2.INTER_AREA)
        self.output_image = None
        self.mask = None

    def switchBackground(self, current_filter):
        filterImagesLib = {
            'painterly': 'IMG_2792.jpg',
            'watercolor': 'IMG_4210.jpg',
            'oil painting': 'IMG_2826.jpg'
        }
        filterImage = filterImagesLib[current_filter]
        imageFullPath = 'smart_canvas/backgrounds/' + filterImage

        self.bg_image = cv2.imread(imageFullPath)
        dim = (1280,720)
        self.bg_image = cv2.resize(self.bg_image, dim, interpolation = cv2.INTER_AREA)
        return self.bg_image

    def remove_isolated_pixels(self, mask):
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel)
        return mask

    def apply(self, frame):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False

        results = self.selfie_segmentation.process(frame)

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        self.mask = self.remove_isolated_pixels(results.segmentation_mask)

        condition = np.stack((self.mask,) * 3, axis=-1) > 0.1
        emptyBg = np.zeros(frame.shape, dtype=np.uint8)
        self.output_image = np.where(condition, frame, emptyBg)
        return self.output_image

    def changeBackground(self, frame, current_filter):
        condition = np.stack((self.mask,) * 3, axis=-1) > 0.1

        self.bg_image = self.switchBackground(current_filter)
        self.output_image = np.where(condition, frame, self.bg_image)
        return self.output_image
