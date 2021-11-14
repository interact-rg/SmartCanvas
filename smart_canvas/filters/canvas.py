import cv2
import numpy as np


def canvas_filter(frame):
    tile = cv2.imread("smart_canvas/filters/struc.pgm")
    width = frame.shape[1]
    height = frame.shape[0]
    x_count = int(width / tile.shape[0]) + 1
    y_count = int(height / tile.shape[1]) + 1

    tiled = np.tile(tile, (y_count, x_count, 1))
    canvas_bg = tiled[0:frame.shape[0], 0:frame.shape[1]]
    kernel = np.array([[0.5, 0], [0, 0.5]])

    canvas_bg = cv2.filter2D(canvas_bg, -1, kernel=kernel)
    alpha = 0.85
    ret_frame = cv2.addWeighted(frame, alpha, canvas_bg, 1 - alpha, 0)
    return ret_frame
