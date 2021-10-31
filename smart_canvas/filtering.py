""" filtering.py """

# Default packages
import itertools

# External packages
import cv2
import numpy as np

# Internal packages


def mosaic_filter(frame):
    width = frame.shape[1]
    height = frame.shape[0]
    rect = (0,0, width, height)
    subdiv = cv2.Subdiv2D(rect)
    for n in range(1000):
        subdiv.insert([np.random.randint(0,width-1), np.random.randint(0,height-1)])

    (facets, centers) = subdiv.getVoronoiFacetList([])
    for i in range(0, len(facets)):
        ifacet_arr = []
        for f in facets[i]:
            ifacet_arr.append(f)
        ifacet = np.array(ifacet_arr, np.int)
        mask = np.full((height, width), 0, dtype=np.uint8)
        cv2.fillConvexPoly(mask, ifacet, (255,255,255))
        ifacets = np.array([ifacet])

        res = cv2.bitwise_or(frame, frame, mask=mask)
        col_mean = cv2.mean(res, mask)

        cv2.fillConvexPoly(frame, ifacet, col_mean)
        #cv2.polylines(img, ifacets, True, (0,0,0), 1)
    return frame

def canvas_filter(frame):
    tile = cv2.imread("smart_canvas/struc.pgm")
    width = frame.shape[1]
    height = frame.shape[0]
    x_count = int(width / tile.shape[0]) + 1
    y_count = int(height / tile.shape[1]) + 1

    tiled = np.tile(tile, (y_count, x_count, 1))
    canvas_bg = tiled[0:frame.shape[0], 0:frame.shape[1]]
    kernel = np.array([[0.5,0],[0,0.5]])

    canvas_bg = cv2.filter2D(canvas_bg, -1, kernel=kernel)
    alpha = 0.85
    frame = cv2.addWeighted(frame, alpha, canvas_bg, 1 - alpha, 0)
    return frame

catalog = {
    'mosaic': mosaic_filter,
    'canvas': canvas_filter
}

carousel = itertools.cycle(catalog)
