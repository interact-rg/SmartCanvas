""" core.py """

# Default packages

# External packages
import cv2
# Internal packages
from . import filtering
from . import background

current_filter = filtering.catalog[next(filtering.carousel)]

def process(frame):
    fgmask = background.foregroundMask(frame)
    handled_frame = current_filter(frame)
    result_frame = cv2.bitwise_and(handled_frame, handled_frame, mask=fgmask)
    return result_frame