import cv2

backSub = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=32, detectShadows=False)

def foregroundMask(frame):
    fgMask = backSub.apply(frame)
    return fgMask