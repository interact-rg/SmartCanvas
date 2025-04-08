from cv2.typing import MatLike
from numpy.typing import ArrayLike
import numpy as np
import cv2
from time import perf_counter

class Filter:
    """Base class for all filters."""
    bg_root: str = "smart_canvas/backgrounds/"
    dimensions: tuple[int, int] = (1280, 720)
    bg_image: MatLike
    background: str|None = None
    timing_samples: list[float] = []
    average_time: float = 0
    
    def __init__(self):
        if self.background is not None:
            bg_img = cv2.imread(self.bg_root + self.background)
        else:
            bg_img = np.zeros((self.dimensions[1], self.dimensions[0], 3), dtype=np.uint8)
        self.bg_image = cv2.resize(bg_img, self.dimensions, interpolation=cv2.INTER_AREA)

    def filter_frame(self, frame: MatLike, mask: MatLike) -> MatLike:
        """ End to end filter function. """
        startTime = perf_counter()
        filtered_frame = self.filter(frame)
        filtered_bg = self.background_filter(frame)
        masked = self.mask_background(filtered_frame, filtered_bg, mask)
        endTime = perf_counter()
        self.timing_samples.append(endTime - startTime)
        if (len(self.timing_samples) > 0):
            self.average_time = float(np.mean(self.timing_samples)) 
        return masked

    def filter(self, frame: MatLike) -> MatLike:
        """ Modifies the frame. """
        return frame

    def background_filter(self, frame: MatLike) -> MatLike:
        """ Modifies the background. """
        return self.bg_image

    def mask_background(self, frame: MatLike, background: MatLike, mask: MatLike):
        """ Masks the background with the given mask. """
        condition: ArrayLike = np.stack((mask, ) * 3, axis=-1) > 0.1

        try:
            output_image = np.where(condition, frame, background)
        except:
            print('[Warn] Frame and background shape mismatch!')
            temp_bg_image = cv2.resize(background, (frame.shape[1], frame.shape[0]))
            output_image = np.where(condition, frame, temp_bg_image)
        return output_image
    
    def get_background(self) -> MatLike:
        """ Returns the background image. """
        if self.bg_image is None:
            return np.zeros((self.dimensions[1], self.dimensions[0], 3), dtype=np.uint8)
        return self.bg_image