import cv2
from smart_canvas.filters.base import Filter

from cv2.typing import MatLike

class OilPainting(Filter):
    background = 'oil_painting_bg.jpg'
    
    def filter(self, frame: MatLike):
        return cv2.xphoto.oilPainting(frame, 7, 1)