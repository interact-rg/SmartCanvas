""" filter_test.py """

import cv2
import pytest
import numpy as np

from smart_canvas.filters.carousel import FilterCarousel


@pytest.fixture()
def carousel():
	yield FilterCarousel()


class TestFilters(object):
	def test_filter_with_image(self, carousel):
		frame = cv2.imread(f"tests/test_assets/small_image/image.png")
		w, h, c = frame.shape
		for _ in carousel.catalog:
			filtered_frame = carousel.current_filter(frame)
			p_w, p_h, p_c = filtered_frame.shape
			assert w == p_w, f'wrong width in: {carousel.current_name}'
			assert h == p_h, f'wrong height in: {carousel.current_name}'
			assert c == p_c, f'wrong amount of color channels in: {carousel.current_name}'
			carousel.next_filter()

	def test_filter_with_black_image(self, carousel):
		frame = np.zeros((50, 50, 3), np.uint8)
		w, h, c = frame.shape
		for _ in carousel.catalog:
			filtered_frame = carousel.current_filter(frame)
			p_w, p_h, p_c = filtered_frame.shape
			assert w == p_w, f'wrong width in: {carousel.current_name}'
			assert h == p_h, f'wrong height in: {carousel.current_name}'
			assert c == p_c, f'wrong amount of color channels in: {carousel.current_name}'
			carousel.next_filter()

	def test_filter_with_white_image(self, carousel):
		frame = np.zeros((50, 50, 3), np.uint8)
		frame[:] = 255
		w, h, c = frame.shape
		for _ in carousel.catalog:
			filtered_frame = carousel.current_filter(frame)
			p_w, p_h, p_c = filtered_frame.shape
			assert w == p_w, f'wrong width in: {carousel.current_name}'
			assert h == p_h, f'wrong height in: {carousel.current_name}'
			assert c == p_c, f'wrong amount of color channels in: {carousel.current_name}'
			carousel.next_filter()

	# TODO: This test breaks alot of filters
	def test_filter_with_min_imagesize(self, carousel):
		frame = (np.random.random((2, 2, 3)) * 255).astype(np.uint8) # min input size
		w, h, c = frame.shape
		for _ in carousel.catalog:
			filtered_frame = carousel.current_filter(frame)
			p_w, p_h, p_c = filtered_frame.shape
			assert w == p_w, f'wrong width in: {carousel.current_name}'
			assert h == p_h, f'wrong height in: {carousel.current_name}'
			assert c == p_c, f'wrong amount of color channels in: {carousel.current_name}'
			carousel.next_filter()

	def test_filter_with_max_imagesize(self, carousel):
		frame = (np.random.random((720, 1280, 3)) * 255).astype(np.uint8) # max camera resolution
		w, h, c = frame.shape
		for _ in carousel.catalog:
			filtered_frame = carousel.current_filter(frame)
			p_w, p_h, p_c = filtered_frame.shape
			assert w == p_w, f'wrong width in: {carousel.current_name}'
			assert h == p_h, f'wrong height in: {carousel.current_name}'
			assert c == p_c, f'wrong amount of color channels in: {carousel.current_name}'
			carousel.next_filter()

	def test_return_type(self, carousel):
		frame = (np.random.random((100, 100, 3)) * 255).astype(np.uint8) 
		for _ in carousel.catalog:
			filtered_frame = carousel.current_filter(frame)
			assert isinstance(filtered_frame, np.ndarray), f'wrong return type in: {carousel.current_name}'
			