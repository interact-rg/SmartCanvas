import math
import cv2
import bisect
import scipy.spatial
import numpy as np
import random

# Internal files
from .color_palette import ColorPalette
from .vector_field import VectorField


def compute_color_probabilities(pixels, palette, k=9):
    distances = scipy.spatial.distance.cdist(pixels, palette.colors)
    maxima = np.amax(distances, axis=1)

    distances = maxima[:, None] - distances
    summ = np.sum(distances, 1)
    distances /= summ[:, None]

    distances = np.exp(k*len(palette)*distances)
    summ = np.sum(distances, 1)
    distances /= summ[:, None]

    return np.cumsum(distances, axis=1, dtype=np.float32)


def color_select(probabilities, palette):
    r = random.uniform(0, 1)
    i = bisect.bisect_left(probabilities, r)
    return palette[i] if i < len(palette) else palette[-1]


def randomized_grid(h, w, scale):
    assert (scale > 0)

    r = scale//2

    grid = []
    for i in range(0, h, scale):
        for j in range(0, w, scale):
            y = random.randint(-r, r) + i
            x = random.randint(-r, r) + j

            grid.append((y % h, x % w))

    random.shuffle(grid)
    return grid




def pointillism(image):

	# setup parameters
	stroke_scale = int(math.ceil(max(image.shape) / 1000))
	gradient_smoothing_radius = int(round(max(image.shape) / 50))

	# convert the image to grayscale to compute the gradient
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# Compute color palette
	palette = ColorPalette.from_image(image, 20) # change second arg to how many colors to use
	palette = palette.extend([(0, 50, 0), (15, 30, 0), (-15, 30, 0)])

	# compute gradient
	gradient = VectorField.from_gradient(gray)
	gradient.smooth(gradient_smoothing_radius)

	# create a "cartonized" version of the image to use as a base for the painting
	result = cv2.medianBlur(image, 11)

	# define a randomized grid of locations for the brush strokes
	grid = randomized_grid(image.shape[0], image.shape[1], scale=3)
	batch_size = 10000

	for h in range(0, len(grid), batch_size):
		# get the pixel colors at each point of the grid
		pixels = np.array([image[x[0], x[1]] for x in grid[h:min(h + batch_size, len(grid))]])
		# precompute the probabilities for each color in the palette
		# lower values of k means more randomnes
		color_probabilities = compute_color_probabilities(pixels, palette, k=9)

		for i, (y, x) in enumerate(grid[h:min(h + batch_size, len(grid))]):
			color = color_select(color_probabilities[i], palette)
			angle = math.degrees(gradient.direction(y, x)) + 90
			length = int(round(stroke_scale + stroke_scale * math.sqrt(gradient.magnitude(y, x))))

			# draw the brush stroke
			cv2.ellipse(result, (x, y), (length, stroke_scale), angle, 0, 360, color, -1, cv2.LINE_AA)

	return result



