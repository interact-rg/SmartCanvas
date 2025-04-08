import cv2
import numpy as np
from cv2.typing import MatLike
from typing import Protocol
from mediapipe.python.solutions.selfie_segmentation import SelfieSegmentation

from time import perf_counter

class Segmentation(Protocol):
    segmentation_mask: MatLike

class ForegroundMask:
    """
    Class that gives the foreground mask.
    """
    timing_samples: list[float] = []
    average_time: float = 0

    def __init__(self):
        self.selfie_segmentation = SelfieSegmentation(model_selection=1)
        self.bg_image = cv2.imread('smart_canvas/backgrounds/painterly_bg.jpg')
        dim = (1280,720)
        self.bg_image = cv2.resize(self.bg_image, dim, )
        self.output_image = None
        self.mask = None


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

        end_time = perf_counter()
        self.timing_samples.append(end_time - start_time)
        if len(self.timing_samples) > 0:
            self.average_time = float(np.mean(self.timing_samples))
        
        return self.mask