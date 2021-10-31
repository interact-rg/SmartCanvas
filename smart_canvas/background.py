import cv2

backSub = cv2.createBackgroundSubtractorMOG2(history=20, varThreshold=16, detectShadows=False)

def foregroundMask(frame):
    fgMask = backSub.apply(frame)
    return fgMask
