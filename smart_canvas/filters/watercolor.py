import cv2

def watercolor(frame):
    return cv2.stylization(frame, sigma_s=60, sigma_r=0.4)
