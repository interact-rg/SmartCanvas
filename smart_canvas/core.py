""" core.py """

# Default packages

# External packages
import cv2
# Internal packages
from . import filtering
from . import background
from . import gestureDetection


class FrameProcessor:
    def __init__(self):
        self.current_filter = filtering.catalog[next(filtering.carousel)]
        self.framecount = 0
        self.pictureframe = None
        self.delaycounter = 0
        self.filtercounter = 0

    def process(self, frame):
        if self.delaycounter > 0:  # show the filtered picture
            self.delaycounter -= 1
            return self.pictureframe
        if self.filtercounter > 0:  # show the current filter when switching
            self.filtercounter -= 1
            cv2.putText(frame, self.current_filter.__name__, (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 5)
            return frame
        if self.framecount < 50:  # make a reference background out of 50 frames
            self.pictureframe = frame
            background.foregroundMask(frame)
        fingercount = gestureDetection.detect_fingercount(frame)
        if fingercount == 2:  # switch filter
            self.current_filter = filtering.catalog[next(filtering.carousel)]
            self.filtercounter = 50
        if fingercount == 5:  # take a picture and process it
            fgmask = background.foregroundMask(frame)
            masked_frame = cv2.bitwise_and(frame, frame, mask=fgmask)
            handled_frame = self.current_filter(masked_frame)
            self.pictureframe = handled_frame
            self.delaycounter = 100
        self.framecount += 1
        return frame
