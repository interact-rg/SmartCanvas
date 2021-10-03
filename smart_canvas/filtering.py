""" filtering.py """

# Default packages
import itertools

# External packages
import cv2

# Internal packages

def filter_oil_painting(frame):
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (6,6))
    morph = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
    result = cv2.normalize(morph, None, 20, 255, cv2.NORM_MINMAX)
    return result

catalog = {
    'oil_painting': lambda x: filter_oil_painting(x),
    'watercolor': lambda x: cv2.stylization(x, sigma_s=60, sigma_r=0.6),
    'gray': lambda x: cv2.cvtColor(x, cv2.COLOR_BGR2GRAY),
    'bw_sketch': lambda x: cv2.pencilSketch(x, sigma_s=60, sigma_r=0.07, shade_factor=0.05)[0],
    'color_sketch': lambda x: cv2.pencilSketch(x, sigma_s=60, sigma_r=0.07, shade_factor=0.05)[1],
    'blur': lambda x: cv2.GaussianBlur(x, (21, 21), 0),
}

carousel = itertools.cycle(catalog)
