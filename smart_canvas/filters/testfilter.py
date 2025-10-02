import cv2
from cv2.typing import MatLike
from smart_canvas.filters.base import Filter


class TestFilter(Filter):
    background = 'testimage.jpg'

    def filter(self, frame: MatLike) -> MatLike:
        image = cv2.blur(frame,(5,5))
        return image

    def background_filter(self, frame: MatLike) -> MatLike:
        output = cv2.GaussianBlur(self.bg_image, (5, 5), 0)
        return output