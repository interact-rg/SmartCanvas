import cv2

from cv2.typing import MatLike

def testfilter(frame: MatLike):
    #frame_grey = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    #image = cv2.GaussianBlur(frame, (3, 3), 0)
    #image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #filtered_image = cv2.Laplacian(image_gray, cv2.CV_16S, ksize=3)
    #laplacian = cv2.Laplacian(frame,cv2.CV_64F)


    #image_grey = cv2.cvtColor(frame, cv2.COLOR_BAYER_RGGB2RGB_EA)

    image = cv2.blur(frame,(5,5))

    return image