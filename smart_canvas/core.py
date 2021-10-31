""" core.py """

# Default packages

# External packages
import cv2
# Internal packages
from . import filtering
from . import background

current_filter = filtering.catalog[next(filtering.carousel)]

def create_background(frame):
    background.foregroundMask(frame)

def process(frame):
    fgmask = background.foregroundMask(frame)
    masked_frame = cv2.bitwise_and(frame, frame, mask=fgmask)
    handled_frame = current_filter(masked_frame)
    return handled_frame
