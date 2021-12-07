""" filter_test.py """

import cv2
import pytest

from smart_canvas.filters.carousel import FilterCarousel


class TestFilters(object):
    def test_filter_with_image(self):
        filters = FilterCarousel()
        frame = cv2.imread(f"tests/test_assets/small_image/image.png")
        w, h, c = frame.shape
        for i in filters.catalog:
            filtered_frame = filters.current_filter(frame)
            p_w, p_h, p_c = filtered_frame.shape
            assert w == p_w
            assert h == p_h
            assert c == p_c
            filters.next_filter()
