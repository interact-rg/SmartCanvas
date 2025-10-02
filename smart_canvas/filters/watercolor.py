import cv2
from smart_canvas.filters.base import Filter

class Watercolor(Filter):
    background = 'watercolor_bg.jpeg'

    def filter(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
        return cv2.stylization(frame, sigma_s=60, sigma_r=0.4)
