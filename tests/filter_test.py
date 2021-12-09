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
            assert w == p_w
            assert h == p_h
            assert c == p_c
            carousel.next_filter()

    def test_filter_with_black_image(self, carousel):
        frame = np.zeros((50, 50, 3), np.uint8)
        w, h, c = frame.shape
        for _ in carousel.catalog:
            filtered_frame = carousel.current_filter(frame)
            p_w, p_h, p_c = filtered_frame.shape
            assert w == p_w
            assert h == p_h
            assert c == p_c
            carousel.next_filter()

    def test_filter_with_white_image(self, carousel):
        frame = np.zeros((50, 50, 3), np.uint8)
        frame[:] = 255
        w, h, c = frame.shape
        for _ in carousel.catalog:
            filtered_frame = carousel.current_filter(frame)
            p_w, p_h, p_c = filtered_frame.shape
            assert w == p_w
            assert h == p_h
            assert c == p_c
            carousel.next_filter()
