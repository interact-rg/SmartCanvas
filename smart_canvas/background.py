import cv2
import numpy as np


class ForegroundMask:
    """
    Class that gives the foreground mask.
    """

    def __init__(self):
        self.back_sub = cv2.createBackgroundSubtractorMOG2(
            history=100, varThreshold=30, detectShadows=False)
        self.fg_mask = None
        self.frame_list = []

    def create_background(self, frame):
        self.frame_list.append(frame)

    def fill_holes(self, mask):
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        len_contour = len (contours)
        contour_list = []
        for i in range(len_contour):
            drawing = np.zeros_like(mask, np.uint8)  # create a black image
            img_contour = cv2.drawContours(drawing, contours, i, (255, 255, 255), -1)
            contour_list.append(img_contour)

        out = sum(contour_list)
        return out

    def remove_isolated_pixels(self, mask):
        kernel = np.ones((7, 7), np.uint8)
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel)
        return closing

    def apply(self, frame):
        for f in self.frame_list:
            self.back_sub.apply(f)
        self.fg_mask = self.back_sub.apply(frame)
        self.fg_mask = self.remove_isolated_pixels(self.fg_mask)
        self.fg_mask = self.fill_holes(self.fg_mask)
        return self.fg_mask
