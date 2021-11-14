# External packages
import cv2
import numpy as np

def makeStroke(brush, x, y, img):
    '''
    add diagonal stroke to list and return for the paintLayer function
    '''
    if x > img.shape[1]-1:
        x = img.shape[1]-1
    if y > img.shape[0]-1:
        y = img.shape[0]-1
    stroke_color = img[y,x]
    stroke_len = np.random.randint(1,8)
    x_0 = x - stroke_len
    y_0 = y - stroke_len
    if x_0 < 0:
        x_0 = 0
    if y_0 < 0:
        y_0 = 0
    stroke = [(x_0,y_0), (x_0 + stroke_len,y_0 + stroke_len), stroke_color.tolist(), brush]

    return stroke

def makeSplineStroke(x, y, brush, img, canvas, gradients):
    '''
    adds a brush stroke to a list and return it for the paintLayer function to paint
    '''
    g_mag, grad_x, grad_y = gradients
    stroke_color = img[y,x]
    stroke_points = [[x, y]]
    lastDx, lastDy = (0,0)

    maxStrokeLength = 16
    minStrokeLength = 6
    # f_c controls the usage of the previous gradient vs the current gradient
    f_c = 1.0

    for i in range(maxStrokeLength):
        if i > minStrokeLength and np.abs(np.sum(img[y,x]) - np.sum(canvas[y,x])) < np.abs(np.sum(img[y,x]) - np.sum(stroke_color)):
            return [stroke_points, stroke_color.tolist(), brush]
        if g_mag[y,x] == 0:
            return [stroke_points, stroke_color.tolist(), brush]
        gy, gx = grad_x[y,x], grad_y[y,x]
        dx=gx
        dy=-gy

        if lastDx * dx + lastDy * dy < 0:
            dx = -dx
            dy = -dy
        dx = f_c * dx + (1-f_c) * lastDx
        dy = f_c * dy + (1 - f_c) * lastDy
        if dx != 0 and dy != 0:
            dx = dx / np.sqrt(dx ** 2 + dy ** 2)
            dy = dy / np.sqrt(dx ** 2 + dy ** 2)
        x, y = int(x + brush * dx), int(y + brush * dy)
        if x > img.shape[1]-1:
            x = img.shape[1]-1
        if y > img.shape[0]-1:
            y = img.shape[0]-1
        lastDx, lastDy = dx, dy

        stroke_points.append([x,y])
    K = [stroke_points, stroke_color.tolist(), brush]
    return K

def paintLayer(canvas, ref_img, brush, gradients):
    '''
    paint a brush layer
    '''
    strokes = []

    # f_g is the parameter to control grid size as a multiple of brush size
    f_g = 1.5
    grid = int(f_g * brush)

    for x in range(0, ref_img.shape[1], grid):
        for y in range(0, ref_img.shape[0], grid):
            s = makeSplineStroke(x,y, brush, ref_img, canvas, gradients)
            strokes.append(s)
    np.random.shuffle(strokes)

    if strokes is not None:
        for s in strokes:
            cv2.polylines(canvas, [np.array(s[0])], isClosed=False, color=s[1], thickness=s[2], lineType=cv2.LINE_AA)

    return canvas

def calcImageGradients(img):
    '''
    Calculate the x and y gradient and gradient magnitude for the image.
    x and y gradients are used to get the painting direction,
    gradient magnitude is used for the length of the stroke
    '''
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img = cv2.GaussianBlur(img, (3,3), sigmaX=1, sigmaY=1)
    grad_x = cv2.Sobel(img, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=5)
    grad_y = cv2.Sobel(img, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=5)

    # code breaks if we don't include these, "index -1072 is out of bounds for axis 1 with size 490" at "if g_mag[y,x] == 0:" in makeSplineStroke()
    grad_x = grad_x / np.max(grad_x)
    grad_y = grad_y / np.max(grad_y)
    grad_magnitude = np.sqrt((grad_x ** 2) + (grad_y ** 2))
    return grad_magnitude, grad_x, grad_y

def painterly_filter(image):
    '''
    paint the final painting by painting layer for each brush size
    '''
    width = image.shape[1]
    height = image.shape[0]
    canvas = np.zeros((height, width,3), dtype=np.uint8)
    gradients = calcImageGradients(image)

    # f_s controls the blur amount of the reference image
    f_s = 1.0
    # small brush sizes are slow to compute
    # large brushes are not precise enough
    # TODO: find a solution for this
    brush_sizes = [8,6,4]

    for brush in brush_sizes:
        ref_img = cv2.GaussianBlur(image, (0,0), sigmaX=f_s*brush, sigmaY=f_s*brush)
        canvas = paintLayer(canvas, ref_img, brush, gradients)

    return canvas