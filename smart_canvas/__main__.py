""" __main__.py """

# Default packages
import time
import argparse

# External packages
import cv2

# Internal packages
from .core import process

def main():
    device = cv2.VideoCapture(0)

    while(True):
        res, frame = device.read()
        if not res:
            break
        processed_frame = process(frame)
        cv2.imshow('output', processed_frame)
        key = cv2.waitKey(1)
        if key == ord('q'): 
            break

    if res:    
        cv2.destroyWindow('output')
    device.release()
    exit(0)

if __name__ == '__main__':
    main()
