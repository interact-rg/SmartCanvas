""" core.py """

# Default packages

# External packages
import cv2
import numpy as np
# Internal packages
from . import filtering
from . import background
from . import gestureDetection

current_filter = filtering.catalog[next(filtering.carousel)]
framecount = 0
pictureframe = None
delaycounter = 0

def create_background(frame):
    background.foregroundMask(frame)

def process(frame):
    global framecount
    global pictureframe
    global delaycounter
    if delaycounter > 0:
        delaycounter -= 1
        return pictureframe
    if framecount < 50:  # make a reference background out of 50 frames
        create_background(frame)
    fingercount = gestureDetection.detect_fingercount(frame)
    if fingercount == 5:  # take a picture and process it
        fgmask = background.foregroundMask(frame)
        masked_frame = cv2.bitwise_and(frame, frame, mask=fgmask)
        handled_frame = current_filter(masked_frame)
        pictureframe = handled_frame
        delaycounter = 100
    framecount += 1
    return frame
