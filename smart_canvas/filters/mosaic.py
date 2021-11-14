import cv2
import numpy as np


def mosaic_filter(frame, randomness=500):
    width = frame.shape[1]
    height = frame.shape[0]
    rect = (0, 0, width, height)
    subdiv = cv2.Subdiv2D(rect)
    for n in range(randomness):
        v = [np.random.randint(0, width-1), np.random.randint(0, height-1)]
        subdiv.insert(v)

    (facets, centers) = subdiv.getVoronoiFacetList([])
    for i in range(0, len(facets)):
        ifacet_arr = []
        for f in facets[i]:
            ifacet_arr.append(f)
        ifacet = np.array(ifacet_arr, np.int64)
        mask = np.full((height, width), 0, dtype=np.uint8)
        cv2.fillConvexPoly(mask, ifacet, (255, 255, 255))
        ifacets = np.array([ifacet])

        res = cv2.bitwise_or(frame, frame, mask=mask)
        col_mean = cv2.mean(res, mask)

        cv2.fillConvexPoly(frame, ifacet, col_mean)
        #cv2.polylines(img, ifacets, True, (0,0,0), 1)
    return frame
