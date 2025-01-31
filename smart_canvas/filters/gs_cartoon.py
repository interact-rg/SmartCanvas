import cv2
from cv2.typing import MatLike


def gs_cartoon_filter(frame: MatLike):
    img_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_style = cv2.stylization(cv2.cvtColor(img_grey, cv2.COLOR_GRAY2BGR), sigma_s=5, sigma_r=0.10)
    
    return img_style

