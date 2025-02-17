import cv2
import numpy as np
from cv2.typing import MatLike
from numpy.typing import ArrayLike
from typing import Protocol
from mediapipe.python.solutions.selfie_segmentation import SelfieSegmentation

from time import perf_counter

class Segmentation(Protocol):
    segmentation_mask: MatLike

class ForegroundMask:
    """
    Class that gives the foreground mask.
    """

    def __init__(self):
        self.selfie_segmentation = SelfieSegmentation(model_selection=1)
        self.bg_image = cv2.imread('smart_canvas/backgrounds/painterly_bg.jpg')
        dim = (1280,720)
        self.bg_image = cv2.resize(self.bg_image, dim, interpolation=cv2.INTER_AREA)
        self.output_image = None
        self.mask = None

    def switchBackground(self, current_filter: str):
        filter_images_lib = {
            'painterly': 'painterly_bg.jpg',
            'watercolor': 'watercolor_bg.jpeg',
            'oil painting': 'oil_painting_bg.jpg',
            'mosaic': 'mosaic_bg.jpeg',
            'grayscale cartoon': 'gs_cartoon_bg_2.jpeg',
            'anime style': 'anime_bg.jpg',
            'pointillism': 'pointillism_bg.jpg'
        }
        filter_image = filter_images_lib[current_filter]
        image_full_path = 'smart_canvas/backgrounds/' + filter_image

        self.bg_image = cv2.imread(image_full_path)
        dim = (1280, 720)
        self.bg_image = cv2.resize(self.bg_image, dim, interpolation = cv2.INTER_AREA)
        return self.bg_image

    def remove_isolated_pixels(self, mask: MatLike):
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_ERODE, kernel)
        return mask

    def apply(self, frame: MatLike):
        start_time = perf_counter()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame.flags.writeable = False

        results: Segmentation = self.selfie_segmentation.process(frame) # type: ignore

        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        self.mask = self.remove_isolated_pixels(results.segmentation_mask)

        condition = np.stack((self.mask,) * 3, axis=-1) > 0.1
        emptyBg = np.zeros(frame.shape, dtype=np.uint8)
        self.output_image = np.where(condition, frame, emptyBg)
        print(f"[Masking]: {perf_counter() - start_time}s")
        return self.output_image

    def changeBackground(self, frame: MatLike, current_filter: str) -> MatLike:
        start_time = perf_counter()
        if self.mask is None:
            raise ValueError("Foreground mask is missing.")
        condition: ArrayLike = np.stack((self.mask,) * 3, axis=-1) > 0.1

        self.bg_image = self.switchBackground(current_filter)
        self.output_image = np.where(condition, frame, self.bg_image)
        print(f"[Background]: {perf_counter() - start_time}s")
        return self.output_image
