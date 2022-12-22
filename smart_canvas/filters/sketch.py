import cv2
import numpy as np


def sketch_filter(frame):
    '''
    sketch = drawing = frame.copy()
    cv2.pencilSketch(frame, sketch, drawing, sigma_s=1, sigma_r=0.01, shade_factor=0.03)
    '''


    img_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
    '''
    img_blur= cv2.GaussianBlur(img_gray, (21, 21), 0, 0)
    sketch = cv2.divide(img_gray, img_blur, scale=256)
    '''
    return img_gray


def drawing_filter(frame):
    sketch = drawing = frame.copy()
    cv2.pencilSketch(frame, sketch, drawing, sigma_s=10, sigma_r=0.01, shade_factor=0.03)
    return drawing
