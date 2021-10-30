""" __main__.py """

# Default packages
import time
import argparse

# External packages
import cv2

# Internal packages
from .core import process
from .core import create_background

def main():
    device = cv2.VideoCapture(0)
    count = 0
    while(True):
        res, frame = device.read()
        if not res:
            break
        if count < 50:  # make a reference background out of 50 frames
            create_background(frame)
        cv2.imshow('output', frame)
        key = cv2.waitKey(1)
        if key == ord('a'):  # take a picture and process it
            processed_frame = process(frame)
            cv2.imshow('output', processed_frame)
            cv2.waitKey(0)
        if key == ord('q'): 
            break
        count += 1

    if res:    
        cv2.destroyWindow('output')
    device.release()
    exit(0)

if __name__ == '__main__':
    main()
