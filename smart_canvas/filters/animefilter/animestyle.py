import numpy as np
import cv2
import torch
from torchvision.transforms.functional import to_tensor, to_pil_image
from PIL import Image

from .model import Generator
from smart_canvas.filters.base import Filter


from cv2.typing import MatLike
TImage = Image.Image

class AnimeFilter(Filter):
	background = 'anime_bg.jpg'

	def __init__(self):
		super().__init__()
		self.device = "cpu" # change to to cuda if available
		self.model="./smart_canvas/filters/animefilter/weights/face_paint_512_v2.pt"
		self.net = Generator()
		self.net.load_state_dict(torch.load(self.model, map_location="cpu"))
		self.net.to(self.device).eval()
		print(f"model weights loaded: {self.model}")


	def filter(self, frame: MatLike) -> MatLike:
		
		original_shape = frame.shape
		# fix for small image test
		if original_shape[0] < 8 or original_shape[1] < 8:
			frame = cv2.resize(frame, (8, 8))

		
		PIL_img = convert_openCV_to_PIL(frame)

		with torch.no_grad():
			image = to_tensor(PIL_img).unsqueeze(0) * 2 - 1
			out_img = self.net(image.to(self.device), False).cpu()
			out_img = out_img.squeeze(0).clip(-1, 1) * 0.5 + 0.5
			out_img = to_pil_image(out_img)

		opencv_img = convert_PIL_to_openCV(out_img)

		filtered_shape = opencv_img.shape
		if filtered_shape != original_shape:
			opencv_img = cv2.resize(opencv_img, (original_shape[0], original_shape[1]), interpolation=cv2.INTER_CUBIC)

		return opencv_img


def convert_openCV_to_PIL(opencv_img: MatLike) -> TImage:
	RGB_img = cv2.cvtColor(opencv_img, cv2.COLOR_BGR2RGB)
	PIL_img: TImage = Image.fromarray(RGB_img)
	return PIL_img

def convert_PIL_to_openCV(PIL_img: MatLike):
	numpy_img = np.array(PIL_img)
	opencv_img = cv2.cvtColor(numpy_img, cv2.COLOR_RGB2BGR) 
	return opencv_img

def gamma_correction(original_img: MatLike, gamma: float=0.4):
	lookUpTable = np.empty((1,256), np.uint8)
	for i in range(256):
		lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255) 
	result = cv2.LUT(original_img, lookUpTable)
	return result


